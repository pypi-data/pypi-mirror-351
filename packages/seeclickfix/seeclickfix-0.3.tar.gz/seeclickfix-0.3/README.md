Python wrapper for the SeeClickFix (FixIt) API.

# Usage

```python
from seeclickfix.client import SeeClickFixClient
from seeclickfix.models.issue import Status


params = {
    "min_lat": 40.02961244400919,
    "min_lng": -76.333590881195,
    "max_lat": 40.04702644421361,
    "max_lng": -76.26908911880496,
    "status": [Status.OPEN],
    "page": 1,
}

async def main():
    client = SeeClickFixClient()
    issues = await client.get_issues(**params)
    for issue in issues.issues:
        print(f"{issue.created_at}: {issue.summary} - {issue.url}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```