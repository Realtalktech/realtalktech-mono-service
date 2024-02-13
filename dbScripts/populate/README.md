# Demo Data Overview for API Responses

This document outlines the expected results in the API responses based on the demo data populated by the `populateDemoData.py` script. The data includes users, posts, comments, upvotes, and vendor references.

## Users

The script inserts four test users with the following details (User IDs start at 1):

1. **Elon Gates**: 
   - User ID: 1
   - Username: elongates
   - Email: elongates@example.com
   - Password: password
   - Company: SuperchargedSoftware
2. **Bill Musk**: 
   - User ID: 2
   - Username: billmusk
   - Email: billmusk@example.com
   - Password: password
   - Company: MacroAdvanced
3. **Mary Barra**: 
   - User ID: 3
   - Username: marybarra
   - Email: marybarra@example.com
   - Password: password
   - Company: General Autos
4. **Kamala Clinton**: 
   - User ID: 4
   - Username: kamalaclinton
   - Email: kamalaclinton@example.com
   - Password: password
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

The script inserts three vendors, with full profiles, and associates them with the "Sales Tools" category:

1. **Salesforce**: CRM Software
2. **HubSpot**: Inbound Marketing and Sales Software
3. **Zendesk Sell**: Sales CRM

When a vendor object is returned, it will contain a link to an S3 object store to access its logo. 

## Categories

All categories from the updated Figma designs (2/10) are inserted into the DBs.
All discover and discuss categories are inserted into the DBs
All industries and interest areas from profile creation are inserted into DBs.

### Discuss Category Mappings

{
   'AI': 1, 
   'Engineering': 2, 
   'Operations': 3, 
   'Marketing': 4, 
   'Sales': 5, 
   'Customer Success': 6, 
   'Data': 7, 
   'Product': 8, 
   'HR & Talent': 9, 
   'Finance': 10, 
   'Leadership/Exec': 11, 
   'Founder': 12, 
   'Community': 13
}

### Discover Category Mappings

{
   'Sales Tools': 1, 
   'Marketing': 2, 
   'Analytics Tools & Software': 3, 
   'CAD & PLM': 4, 
   'Collaboration & Productivity': 5, 
   'Commerce': 6, 
   'Content Management': 7, 
   'Customer Service': 8, 
   'Data Privacy': 9,
   'Design': 10,
   'Development': 11, 
   'Digital Advertising Tech': 12, 
   'ERP': 13, 
   'Governance, Risk & Compliance': 14, 
   'Hosting': 15, 
   'HR': 16, 
   'IT Infrastructure': 17, 
   'IT Management': 18, 
   'Security': 19, 
   'Supply Chains & Logistics': 20, 
   'Vertical Industry': 21
}

## API Responses

Based on the above data, API responses will reflect the following:

- User details including names, companies, and user IDs.
- Post details including the creator (with user ID for non-anonymous posts), title, body, tagged vendors, and creation time.
- Comment details on each post, including the commenter's user ID and the comment text.
- Upvote information indicating which users have liked comments or posts.

Please note that the actual response structure will depend on the specific API endpoint being called and the query parameters provided.

---

_This README is intended to guide developers and users in understanding the structure and content of the API responses based on the demo data._
