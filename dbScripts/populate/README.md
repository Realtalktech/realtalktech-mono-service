# Demo Data Overview for API Responses

This document outlines the expected results in the API responses based on the demo data populated by the `populateDemoData.py` script. The data includes users, posts, comments, upvotes, and vendor references.

## Users

The script inserts four test users with the following details (User IDs start at 1):

1. **Elon Gates**: 
   - User ID: 1
   - Company: SuperchargedSoftware
2. **Bill Musk**: 
   - User ID: 2
   - Company: MacroAdvanced
3. **Mary Barra**: 
   - User ID: 3
   - Company: General Autos
4. **Kamala Clinton**: 
   - User ID: 4
   - Company: Capitol Tech

## Posts

The script creates four posts with different characteristics:

1. **Post by Elon Gates about Salesforce**:
   - Post ID: 1
   - Tags: Salesforce
   - Comments: From Bill Musk and Mary Barra
   - Elon Gates (User ID: 1) likes Bill's comment

2. **Post by Elon Gates about HubSpot**:
   - Post ID: 2
   - Tags: HubSpot
   - Comments: From Mary Barra
   - Bill Musk (User ID: 2) likes the comment

3. **Anonymous Post by Elon Gates**:
   - Post ID: 3
   - Anonymous: Yes
   - Comments: From Bill Musk

4. **Post by Elon Gates about Zendesk Sell**:
   - Post ID: 4
   - Tags: Zendesk Sell
   - Comments: From Kamala Clinton
   - Elon Gates (User ID: 1) likes the comment

## Vendors

The script inserts three vendors and associates them with the "Sales Tools" category:

1. **Salesforce**: CRM Software
2. **HubSpot**: Inbound Marketing and Sales Software
3. **Zendesk Sell**: Sales CRM

## Categories

Multiple categories are inserted, including "AI", "Engineering", "Operations", etc. These categories are used to tag posts and associate user interests.

## API Responses

Based on the above data, API responses will reflect the following:

- User details including names, companies, and user IDs.
- Post details including the creator (with user ID for non-anonymous posts), title, body, tagged vendors, and creation time.
- Comment details on each post, including the commenter's user ID and the comment text.
- Upvote information indicating which users have liked comments or posts.

Please note that the actual response structure will depend on the specific API endpoint being called and the query parameters provided.

---

_This README is intended to guide developers and users in understanding the structure and content of the API responses based on the demo data._
