# WarcraftLogs API Notes

## Access Token

The access token is a JWT token that is used to authenticate requests to the WarcraftLogs API. It can be obtained by making a POST request with the following multipart form data to the token URI `https://www.warcraftlogs.com/oauth/token`:

```python
token_data = {
    "grant_type": "client_credentials",
    "client_id": self.client_id,
    "client_secret": self.client_secret,
}

response = requests.post(self.token_url, data=token_data)

return response.json()["access_token"]
```

More details on the access token can be found in the API docs at `https://www.archon.gg/wow/articles/help/api-documentation#access-token`.

## Queries

Queries are made to the API using the GraphQL API. The API docs provide a schema for the queries that can be made.

The schema is available at `https://www.warcraftlogs.com/v2-api-docs/warcraft/query.doc.html`.

In Python, we can use the `requests` library to make the queries.

```python
access_token = "your_access_token"

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
}

query = """
query {
    ... your query ...
}
"""

response = requests.post(
    self.api_url, json={"query": query}, headers=headers
)
return response.json()
```

### Report Metadata

To access a specific report, first we need to get the report code from the URL. The report code is the last part of the URL after the `/reports/` path.

For example, the report code for `https://www.warcraftlogs.com/reports/abc123def456` is `abc123def456`.

Once we have the report code, we can use it to get the report metadata. The GraphQL docs are pretty finnicky, so pasted below is a lot of available data that can be fetched.

```graphql
query {
	reportData {
		report(code: "abcd123def456") {
			title
			startTime
			endTime
			owner { name }
			zone { name }
            code
            region {
                id 
                name
                compactName
            }
            guild{
                id
                name 
            }
            fights (killType: Encounters){
                id
                encounterID
                name
                kill
                endTime
                startTime
                size
                originalEncounterID
            }
            rankedCharacters {
                id
                canonicalID
                name
                classID
                level
                
            }
            masterData(translate: true) {
                actors(type: "Player") {
                    id
                    gameID
                    server
                    subType
                    name
                }
            }
		}
	}
}
```

## Report Participants

To get the participants of a report, we can use the `rankedCharacters` field. 

Here is an example of output from a query for `rankedCharacters` that looks like this:

```graphql
query {
	reportData {
		report(code: "J3YQw9pyAhxB8avG") {
			title
			startTime
			endTime
			rankedCharacters {
				id
				canonicalID
				name
				classID
				level
			}
		}
	}
}
```

The output looks like this:

```json
{
	"data": {
		"reportData": {
			"report": {
				"title": "DS 25m 7/17",
				"startTime": 1752806050551,
				"endTime": 1752813481778,
				"rankedCharacters": [
					{
						"id": 63063534,
						"canonicalID": 63063534,
						"name": "Tyrindor",
						"classID": 11,
						"level": 72
					},
					{
						"id": 66877293,
						"canonicalID": 66877293,
						"name": "Glitterus",
						"classID": 8,
						"level": 0
					},
					{
						"id": 82747846,
						"canonicalID": 82747846,
						"name": "Khaosghost",
						"classID": 6,
						"level": 0
					},
					{
						"id": 97760654,
						"canonicalID": 97760654,
						"name": "Goofberry",
						"classID": 7,
						"level": 85
					},
					{
						"id": 97760843,
						"canonicalID": 97760843,
						"name": "Kevgore",
						"classID": 9,
						"level": 0
					},
					{
						"id": 97760845,
						"canonicalID": 97760845,
						"name": "Khalnaras",
						"classID": 2,
						"level": 0
					},
					{
						"id": 97760857,
						"canonicalID": 97760857,
						"name": "Rocksdruid",
						"classID": 2,
						"level": 0
					},
					{
						"id": 97841403,
						"canonicalID": 97841403,
						"name": "Resgarloth",
						"classID": 6,
						"level": 0
					},
					{
						"id": 98186437,
						"canonicalID": 98186437,
						"name": "Notbang",
						"classID": 1,
						"level": 0
					},
					{
						"id": 98327130,
						"canonicalID": 98327130,
						"name": "Sabrehawk",
						"classID": 9,
						"level": 85
					},
					{
						"id": 98456227,
						"canonicalID": 98456227,
						"name": "Krakoda",
						"classID": 3,
						"level": 0
					},
					{
						"id": 98561192,
						"canonicalID": 98561192,
						"name": "Iroxxiar",
						"classID": 5,
						"level": 85
					},
					{
						"id": 98561194,
						"canonicalID": 98561194,
						"name": "Kelthuzaddy",
						"classID": 4,
						"level": 85
					},
					{
						"id": 98561195,
						"canonicalID": 98561195,
						"name": "Lightninrock",
						"classID": 9,
						"level": 0
					},
					{
						"id": 98561203,
						"canonicalID": 98561203,
						"name": "Babyflower",
						"classID": 10,
						"level": 0
					},
					{
						"id": 98561205,
						"canonicalID": 98561205,
						"name": "Chiipmon",
						"classID": 3,
						"level": 0
					},
					{
						"id": 98561206,
						"canonicalID": 98561206,
						"name": "Caelcormac",
						"classID": 8,
						"level": 0
					},
					{
						"id": 98718303,
						"canonicalID": 98718303,
						"name": "Silentpaw",
						"classID": 5,
						"level": 0
					},
					{
						"id": 98718304,
						"canonicalID": 98718304,
						"name": "Sopersana",
						"classID": 7,
						"level": 0
					},
					{
						"id": 98718305,
						"canonicalID": 98718305,
						"name": "Kaylestal",
						"classID": 3,
						"level": 0
					},
					{
						"id": 98718308,
						"canonicalID": 98718308,
						"name": "Bobbypunch",
						"classID": 5,
						"level": 0
					},
					{
						"id": 98861254,
						"canonicalID": 98861254,
						"name": "Discrasia",
						"classID": 10,
						"level": 0
					},
					{
						"id": 98861255,
						"canonicalID": 98861255,
						"name": "Azarla",
						"classID": 7,
						"level": 0
					},
					{
						"id": 98861256,
						"canonicalID": 98861256,
						"name": "Beeftitz",
						"classID": 11,
						"level": 0
					},
					{
						"id": 98861257,
						"canonicalID": 98861257,
						"name": "Facelessguy",
						"classID": 9,
						"level": 0
					}
				]
			}
		}
	}
}
```