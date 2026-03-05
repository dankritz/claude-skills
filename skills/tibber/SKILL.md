---
name: tibber
description: Query the Tibber electricity API to analyze power consumption, costs, and price trends. Use when the user wants to explore energy usage, electricity costs, price forecasts, or consumption patterns from their Tibber account.
allowed-tools: Bash,Read,Write,Edit,WebFetch
---

# Tibber Energy Analysis Skill

## Overview

This skill queries the Tibber GraphQL API to help analyze electricity consumption, costs, and pricing trends over time.

**API Endpoint:** `https://api.tibber.com/v1-beta/gql`
**Auth:** Bearer token in `Authorization` header
**API Key location:** `.env` file in the skill directory (`skills/tibber/.env`)

---

## Setup

The API token is stored in the `.env` file. **Use the Read tool** to read it, then extract the token value. The file is at:

```
/Users/dan.kritzinger/git/claude-skills/skills/tibber/.env
```

Read the file, find the line `TIBBER_TOKEN=...`, and use that token value directly in the `Authorization` header of every curl command. Do not use shell `source` or environment variables — inline the token value directly.

---

## Making Queries

Use `curl` to call the GraphQL endpoint, with the token value inlined directly:

```bash
curl -s -X POST https://api.tibber.com/v1-beta/gql \
  -H "Authorization: Bearer TOKEN_VALUE_HERE" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ viewer { homes { id address { address1 city } } } }"}'
```

Parse JSON output with `jq` for readable results.

---

## Key GraphQL Queries

### List homes
```graphql
{
  viewer {
    homes {
      id
      address {
        address1
        postalCode
        city
        country
      }
    }
  }
}
```

### Consumption data (with cost)
```graphql
{
  viewer {
    homes {
      consumption(resolution: HOURLY, last: 48) {
        nodes {
          from
          to
          cost
          unitPrice
          unitPriceVAT
          consumption
          consumptionUnit
          currency
        }
      }
    }
  }
}
```

**Resolution options:** `HOURLY` | `DAILY` | `WEEKLY` | `MONTHLY` | `ANNUAL`

### Current electricity price
```graphql
{
  viewer {
    homes {
      currentSubscription {
        priceInfo {
          current {
            total
            energy
            tax
            startsAt
            level
          }
          today {
            total
            energy
            tax
            startsAt
            level
          }
          tomorrow {
            total
            energy
            tax
            startsAt
            level
          }
        }
      }
    }
  }
}
```

### Full home details (consumption + prices)
```graphql
{
  viewer {
    homes {
      id
      address {
        address1
        city
        country
      }
      consumption(resolution: DAILY, last: 30) {
        nodes {
          from
          to
          cost
          unitPrice
          consumption
          currency
        }
      }
      currentSubscription {
        priceInfo {
          current {
            total
            level
            startsAt
          }
        }
      }
    }
  }
}
```

---

## Analysis Workflow

When the user asks about energy trends, costs, or consumption:

1. **Read the token** — use the Read tool on `/Users/dan.kritzinger/git/claude-skills/skills/tibber/.env`, extract the `TIBBER_TOKEN` value, and inline it into curl commands
2. **Fetch data** using the appropriate query and resolution
3. **Parse with jq** to extract relevant fields
4. **Analyze trends** — look for:
   - Peak consumption hours/days
   - Cost per kWh over time
   - Total spend by day/week/month
   - Correlation between price level and usage
5. **Present findings** clearly with numbers and patterns highlighted

### Example: Monthly cost breakdown
```bash
curl -s -X POST https://api.tibber.com/v1-beta/gql \
  -H "Authorization: Bearer $TIBBER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ viewer { homes { consumption(resolution: MONTHLY, last: 12) { nodes { from to cost consumption currency } } } } }"}' \
  | jq '.data.viewer.homes[0].consumption.nodes[] | {month: .from, cost: .cost, kwh: .consumption, currency: .currency}'
```

### Example: Today's hourly usage
```bash
curl -s -X POST https://api.tibber.com/v1-beta/gql \
  -H "Authorization: Bearer $TIBBER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ viewer { homes { consumption(resolution: HOURLY, last: 24) { nodes { from to cost consumption unitPrice } } } } }"}' \
  | jq '.data.viewer.homes[0].consumption.nodes[]'
```

---

## Tips

- `last: N` fetches the N most recent records for the given resolution
- `cost` is the total cost for the interval (in the home's currency)
- `consumption` is kWh used in the interval
- `unitPrice` is the price per kWh paid (varies with spot price)
- `level` in price info can be: `VERY_CHEAP` | `CHEAP` | `NORMAL` | `EXPENSIVE` | `VERY_EXPENSIVE`
- If a home has no smart meter, consumption data may be unavailable
