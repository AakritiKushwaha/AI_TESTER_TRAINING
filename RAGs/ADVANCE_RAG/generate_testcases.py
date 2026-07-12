"""Generate 5,000 realistic VWO (Visual Website Optimizer) test cases in JIRA CSV format."""

import csv
import os
import random
from typing import List, Dict

random.seed(42)

MODULES = [
    "Campaign Management", "User Segmentation", "Reporting & Analytics",
    "Integrations", "Account Settings", "User Management", "Billing",
    "API & Webhooks", "Audience Targeting", "Personalization"
]

TEMPLATES = {
    "Campaign Management": [
        {
            "title": "Verify A/B campaign creation with {n} variations",
            "steps": "1. Navigate to Campaigns > New Campaign\n2. Select A/B testing type\n3. Add {n} variations with different content\n4. Set traffic allocation to {traffic}%\n5. Save and launch campaign",
            "expected": "Campaign created successfully with {n} variations. Traffic split correctly across variations.",
            "tags": "campaign,ab-testing,creation,smoke"
        },
        {
            "title": "Validate campaign scheduling with start and end dates",
            "steps": "1. Create a new campaign\n2. Set start date to tomorrow\n3. Set end date to 30 days from start\n4. Set goal as 'conversion_rate'\n5. Save and verify campaign status",
            "expected": "Campaign is scheduled correctly. Status shows 'Scheduled'. Campaign auto-stops on end date.",
            "tags": "campaign,scheduling,regression"
        },
        {
            "title": "Test campaign pause and resume functionality",
            "steps": "1. Launch an active campaign\n2. Click Pause from campaign actions\n3. Verify campaign status changes to Paused\n4. Wait 5 minutes\n5. Click Resume\n6. Verify campaign resumes with original settings",
            "expected": "Campaign pauses immediately with status 'Paused'. Resume restores original configuration and traffic.",
            "tags": "campaign,lifecycle,pause,resume"
        },
        {
            "title": "Verify campaign cloning preserves all settings",
            "steps": "1. Create a campaign with variations, goals, and targeting\n2. Click Clone from campaign actions\n3. Enter new name for cloned campaign\n4. Save cloned campaign\n5. Compare original and cloned settings",
            "expected": "Cloned campaign has identical settings except name. All variations, goals, and targeting rules preserved.",
            "tags": "campaign,clone,regression"
        },
        {
            "title": "Validate campaign deletion and restore",
            "steps": "1. Navigate to active campaign\n2. Delete the campaign\n3. Verify it moves to Trash\n4. Navigate to Trash\n5. Restore the campaign\n6. Verify all settings are intact",
            "expected": "Campaign moves to Trash on delete. Restore brings back campaign with all original settings and traffic.",
            "tags": "campaign,deletion,restore,trash"
        },
        {
            "title": "Test campaign with {n}% traffic allocation on mobile devices",
            "steps": "1. Create a new campaign\n2. Set device targeting to Mobile only\n3. Set traffic allocation to {traffic}%\n4. Add {n} variations\n5. Launch and verify mobile traffic split",
            "expected": "Campaign runs only on mobile devices. Traffic is split {traffic}% as configured.",
            "tags": "campaign,mobile,targeting,traffic"
        },
        {
            "title": "Verify goal tracking for click-based campaigns",
            "steps": "1. Create a campaign with Click goal type\n2. Set CSS selector for click tracking\n3. Launch campaign\n4. Perform click events on target element\n5. Verify goal tracking in Reports",
            "expected": "Each click on target element is recorded. Goal conversion data appears in real-time dashboard.",
            "tags": "campaign,goals,click-tracking,analytics"
        },
        {
            "title": "Validate campaign with multiple goals",
            "steps": "1. Create a campaign\n2. Add Goal 1: Click tracking on CTA button\n3. Add Goal 2: Page visit\n4. Add Goal 3: Revenue tracking\n5. Launch and trigger all goal events\n6. Check goal tracking",
            "expected": "All three goals track independently. Dashboard shows separate conversion rates per goal.",
            "tags": "campaign,goals,multi-goal,regression"
        },
        {
            "title": "Test campaign URL targeting with regex patterns",
            "steps": "1. Create campaign with URL targeting\n2. Set URL pattern as /pricing/*|/features/*\n3. Add exclude rule for /blog/*\n4. Launch campaign\n5. Visit matching and non-matching URLs\n6. Verify campaign fires correctly",
            "expected": "Campaign triggers on /pricing/* and /features/*. Does not trigger on /blog/* pages.",
            "tags": "campaign,targeting,url,regex"
        },
        {
            "title": "Verify campaign winner auto-selection after {n} days",
            "steps": "1. Create campaign with auto-select winner option\n2. Set duration to {n} days\n3. Set minimum confidence to 95%\n4. Launch and let run for {n} days\n5. Check winner selection status",
            "expected": "After {n} days, campaign auto-selects the winning variation if 95% confidence is reached.",
            "tags": "campaign,auto-winner,confidence,regression"
        },
    ],
    "User Segmentation": [
        {
            "title": "Verify creating a segment based on user location",
            "steps": "1. Navigate to Audiences > Segments\n2. Create new segment\n3. Add condition: Country equals 'United States'\n4. Add condition: City equals 'New York'\n5. Save segment\n6. Apply segment to a campaign",
            "expected": "Segment created with location conditions. Campaign shows only to users matching both conditions.",
            "tags": "segmentation,location,targeting"
        },
        {
            "title": "Test behavioral segmentation based on past purchases",
            "steps": "1. Create segment with behavioral conditions\n2. Set: Total purchases > 3\n3. Set: Last purchase within 30 days\n4. Set: Average order value > $50\n5. Save and preview matching users\n6. Apply to campaign",
            "expected": "Segment captures users with 3+ purchases, recent activity, and $50+ AOV. Preview shows matching users.",
            "tags": "segmentation,behavioral,purchase,advanced"
        },
        {
            "title": "Validate segmentation with AND/OR logic combinations",
            "steps": "1. Create segment with multiple conditions\n2. Add Group A: (Country = US AND Device = Mobile)\n3. Add Group B: (Country = UK AND Browser = Chrome)\n4. Set Groups OR logic\n5. Save segment\n6. Test with various user profiles",
            "expected": "Segment matches users in Group A OR Group B. Complex logical combinations work correctly.",
            "tags": "segmentation,logic,and-or,advanced"
        },
        {
            "title": "Test session-based segmentation rules",
            "steps": "1. Create segment with session conditions\n2. Set: Number of sessions > 5\n3. Set: Session duration > 120 seconds\n4. Set: Pages per session > 3\n5. Save and apply to campaign\n6. Verify with test users",
            "expected": "Segment correctly identifies high-engagement users based on session metrics.",
            "tags": "segmentation,session,engagement"
        },
        {
            "title": "Verify custom dimension segmentation",
            "steps": "1. Navigate to Segments > Custom Dimensions\n2. Create custom dimension: 'membership_tier'\n3. Create segment: membership_tier equals 'Premium'\n4. Apply to campaign\n5. Test with Premium vs Free users",
            "expected": "Only Premium tier users see the campaign variation. Custom dimensions work across segments.",
            "tags": "segmentation,custom-dimension,premium"
        },
        {
            "title": "Test segment exclusion rules",
            "steps": "1. Create segment: New Visitors\n2. Add exclusion: Exclude users from 'Returning Visitors' segment\n3. Apply to campaign\n4. Test with new and returning users",
            "expected": "Campaign runs only for new visitors. Returning visitors are excluded from the campaign.",
            "tags": "segmentation,exclusion,visitors"
        },
        {
            "title": "Verify segmentation by traffic source",
            "steps": "1. Create segment for traffic source\n2. Set condition: Source equals 'Google'\n3. Set condition: Medium equals 'cpc'\n4. Set condition: Campaign equals 'summer_sale'\n5. Save and apply\n6. Test with various traffic sources",
            "expected": "Only users from Google CPC 'summer_sale' campaign trigger the campaign.",
            "tags": "segmentation,traffic-source,utm,campaign"
        },
        {
            "title": "Test time-based segmentation",
            "steps": "1. Create segment with time conditions\n2. Set: Day of week = Monday-Friday\n3. Set: Time of day = 9:00-17:00\n4. Save segment\n5. Apply to campaign\n6. Test during and outside specified hours",
            "expected": "Campaign runs only on weekdays during business hours (9AM-5PM).",
            "tags": "segmentation,time-based,schedule"
        },
        {
            "title": "Validate recency-based user segmentation",
            "steps": "1. Create segment: First visit within last 7 days\n2. Set page views > 1\n3. Set session count = 1\n4. Save as 'New Interested Users'\n5. Apply to campaign\n6. Test user matching",
            "expected": "Segment captures first-time visitors from last 7 days who explored beyond one page.",
            "tags": "segmentation,recency,new-users"
        },
        {
            "title": "Test segment preview accuracy",
            "steps": "1. Create a complex segment with 5+ conditions\n2. Click Preview to see matching users\n3. Note user count\n4. Modify one condition\n5. Preview again\n6. Compare results",
            "expected": "Preview accurately reflects changes. User count updates dynamically as conditions change.",
            "tags": "segmentation,preview,accuracy,smoke"
        },
    ],
    "Reporting & Analytics": [
        {
            "title": "Verify real-time dashboard metrics accuracy",
            "steps": "1. Launch an A/B campaign\n2. Visit test pages with variations\n3. Perform conversion actions\n4. Navigate to Reports > Dashboard\n5. Compare real-time metrics with expected values\n6. Verify lift and confidence calculations",
            "expected": "Dashboard shows accurate visitor counts, conversion rates, lift percentage, and statistical confidence.",
            "tags": "reporting,dashboard,real-time,accuracy"
        },
        {
            "title": "Test report export to CSV format",
            "steps": "1. Navigate to any campaign report\n2. Click Export > CSV\n3. Wait for export to complete\n4. Open downloaded CSV\n5. Verify column headers and data accuracy\n6. Check date range filtering",
            "expected": "CSV exports with correct headers, all metric columns, and accurate data for selected date range.",
            "tags": "reporting,export,csv,data"
        },
        {
            "title": "Verify statistical significance computation",
            "steps": "1. Run campaign with {n} visitors per variation\n2. Generate {conversions} conversions on variation A\n3. Generate {conversions2} conversions on variation B\n4. Check confidence and significance values\n5. Compare against manual calculation",
            "expected": "Statistical significance computed correctly. Confidence level matches expected probability.",
            "tags": "reporting,statistics,significance,accuracy"
        },
        {
            "title": "Test segmented report filtering",
            "steps": "1. Open campaign report\n2. Apply filter: Device = Mobile\n3. Note metrics\n4. Apply additional filter: Country = US\n5. Compare filtered vs unfiltered data\n6. Clear filters and verify reset",
            "expected": "Reports filter correctly by segment. Nested filters work in combination. Reset clears all filters.",
            "tags": "reporting,filters,segmentation,analytics"
        },
        {
            "title": "Validate revenue tracking reports",
            "steps": "1. Configure revenue tracking on campaign\n2. Add revenue events with known values (${revenue} per conversion)\n3. Trigger {n} conversion events\n4. Navigate to Revenue Report\n5. Verify total revenue calculation\n6. Check per-variation revenue split",
            "expected": "Total revenue = ${total_revenue}. Revenue correctly attributed to variations based on conversion source.",
            "tags": "reporting,revenue,tracking,analytics"
        },
        {
            "title": "Test report date range presets and custom ranges",
            "steps": "1. Open campaign report\n2. Select 'Last 7 days' preset\n3. Verify date range\n4. Select 'Last 30 days' preset\n5. Set custom range: specific start and end dates\n6. Verify all ranges return correct data",
            "expected": "Preset date ranges work correctly. Custom date range accepts valid dates and filters data appropriately.",
            "tags": "reporting,date-range,filter,analytics"
        },
        {
            "title": "Verify heatmap and click map reports",
            "steps": "1. Open a campaign with click tracking\n2. Generate test clicks at known page positions\n3. Navigate to Reports > Heatmap\n4. Verify click density at expected positions\n5. Check click count matches total clicks\n6. Test scroll depth reporting",
            "expected": "Heatmap shows click density at correct positions. Click count matches generated test data.",
            "tags": "reporting,heatmap,click-map,visualization"
        },
        {
            "title": "Test goal funnel visualization",
            "steps": "1. Create campaign with multi-step goal funnel\n2. Define steps: Homepage > Product > Cart > Checkout > Thank You\n3. Simulate user journeys through funnel\n4. Open Funnel Report\n5. Verify drop-off rates at each step\n6. Check conversion path",
            "expected": "Funnel visualization shows correct user counts at each step. Drop-off rates calculated accurately.",
            "tags": "reporting,funnel,visualization,goals"
        },
        {
            "title": "Validate scheduled report delivery via email",
            "steps": "1. Navigate to Reports > Scheduled Reports\n2. Create new schedule\n3. Set frequency: Weekly on Monday\n4. Set recipients: test@example.com\n5. Select format: PDF\n6. Save schedule\n7. Wait for delivery time",
            "expected": "Scheduled report triggers at configured time. Email delivered with correct PDF attachment.",
            "tags": "reporting,schedule,email,delivery"
        },
        {
            "title": "Test API export of report data",
            "steps": "1. Generate API key for report access\n2. Call GET /api/v1/reports/{{campaign_id}}\n3. Set query parameters: date_from, date_to, metrics\n4. Parse API response\n5. Compare with UI report data\n6. Test error handling for invalid parameters",
            "expected": "API returns report data matching UI display. Proper error responses for invalid parameters.",
            "tags": "reporting,api,export,integration"
        },
    ],
    "Integrations": [
        {
            "title": "Verify Google Analytics 4 integration setup",
            "steps": "1. Navigate to Integrations > GA4\n2. Click Connect to Google Analytics\n3. Log in with Google account\n4. Select GA4 property\n5. Grant required permissions\n6. Verify connection status shows Connected",
            "expected": "GA4 integration connects successfully. Goals and events sync between VWO and GA4.",
            "tags": "integrations,google-analytics,ga4,setup"
        },
        {
            "title": "Test Shopify integration for e-commerce tracking",
            "steps": "1. Navigate to Integrations > Shopify\n2. Install VWO app from Shopify App Store\n3. Authenticate and connect store\n4. Create campaign targeting Shopify pages\n5. Launch and verify tracking on store\n6. Check revenue data sync",
            "expected": "Shopify integration installs correctly. Campaigns run on store pages. Revenue data syncs bidirectionally.",
            "tags": "integrations,shopify,ecommerce,tracking"
        },
        {
            "title": "Validate WordPress plugin integration",
            "steps": "1. Download VWO WordPress plugin\n2. Install plugin on WordPress site\n3. Enter Account ID for authentication\n4. Verify plugin activates without errors\n5. Create a campaign\n6. Check snippet injection on WordPress pages",
            "expected": "Plugin activates successfully. SmartCode injects correctly. Campaigns render on WordPress pages.",
            "tags": "integrations,wordpress,plugin,cms"
        },
        {
            "title": "Test HubSpot CRM integration for lead tracking",
            "steps": "1. Navigate to Integrations > HubSpot\n2. Click Connect\n3. Log in to HubSpot account\n4. Select CRM properties to sync\n5. Configure lead scoring integration\n6. Verify data flow from VWO to HubSpot",
            "expected": "HubSpot connects successfully. Visitor data and conversions sync to HubSpot CRM contacts.",
            "tags": "integrations,hubspot,crm,leads"
        },
        {
            "title": "Verify Segment integration for data pipeline",
            "steps": "1. Go to Integrations > Segment\n2. Enter Segment Write Key\n3. Configure events to forward\n4. Enable integration\n5. Run a campaign with conversions\n6. Check Segment debugger for incoming events",
            "expected": "Segment integration forwards all configured VWO events to Segment pipeline using correct schema.",
            "tags": "integrations,segment,data-pipeline,events"
        },
        {
            "title": "Test Zapier integration for workflow automation",
            "steps": "1. Navigate to Integrations > Zapier\n2. Click Create Zap\n3. Select VWO as trigger app\n4. Choose trigger: New Campaign Started\n5. Select action app: Slack\n6. Configure and test Zap",
            "expected": "Zapier integration triggers workflows when VWO events occur. Automated actions execute correctly.",
            "tags": "integrations,zapier,automation,workflow"
        },
        {
            "title": "Validate Google Tag Manager integration",
            "steps": "1. Go to Integrations > GTM\n2. Copy VWO container snippet\n3. Add snippet to GTM container\n4. Publish GTM container\n5. Preview and verify VWO tag fires\n6. Test campaign rendering via GTM",
            "expected": "GTM integration loads VWO correctly. Campaign variations render using GTM-delivered SmartCode.",
            "tags": "integrations,gtm,tag-manager,deployment"
        },
        {
            "title": "Test Facebook Pixel integration",
            "steps": "1. Navigate to Integrations > Facebook\n2. Enter Facebook Pixel ID\n3. Configure events to track (ViewContent, Purchase)\n4. Enable integration\n5. Trigger test events on campaign\n6. Check Facebook Events Manager",
            "expected": "Facebook Pixel fires correctly. Events appear in Facebook Events Manager with correct parameters.",
            "tags": "integrations,facebook,pixel,events"
        },
        {
            "title": "Verify custom webhook integration for real-time data",
            "steps": "1. Navigate to Integrations > Webhooks\n2. Create new webhook\n3. Enter endpoint URL\n4. Select events: campaign.started, variation.won\n5. Set format: JSON\n6. Test webhook with sample event",
            "expected": "Webhook fires POST requests with correct JSON payload on configured events. Endpoint receives data.",
            "tags": "integrations,webhook,custom,real-time"
        },
        {
            "title": "Test multi-integration data consistency",
            "steps": "1. Connect GA4, HubSpot, and Segment simultaneously\n2. Run a campaign with 100 conversions\n3. Check conversion count in VWO dashboard\n4. Compare with GA4\n5. Compare with HubSpot\n6. Compare with Segment\n7. Verify consistency across all platforms",
            "expected": "Conversion counts are consistent (±1%) across VWO, GA4, HubSpot, and Segment integrations.",
            "tags": "integrations,consistency,multi-platform,data"
        },
    ],
    "Account Settings": [
        {
            "title": "Verify account profile update functionality",
            "steps": "1. Navigate to Account > Profile\n2. Update first name\n3. Update last name\n4. Change email address\n5. Save changes\n6. Log out and log back in with new email\n7. Verify profile reflects all changes",
            "expected": "Profile updates save successfully. Email change triggers verification. New email works for login.",
            "tags": "account,profile,settings,smoke"
        },
        {
            "title": "Test password change workflow",
            "steps": "1. Navigate to Account > Security\n2. Enter current password\n3. Enter new strong password\n4. Confirm new password\n5. Save changes\n6. Log out\n7. Log in with new password\n8. Log in with old password (should fail)",
            "expected": "Password changes successfully. New password works. Old password is rejected with error message.",
            "tags": "account,security,password,authentication"
        },
        {
            "title": "Validate two-factor authentication setup",
            "steps": "1. Navigate to Account > Security > 2FA\n2. Choose authenticator app method\n3. Scan QR code with authenticator\n4. Enter 6-digit code from app\n5. Verify 2FA is enabled\n6. Log out and log in with 2FA code\n7. Test recovery codes",
            "expected": "2FA setup completes successfully. Login requires 2FA code. Recovery codes work as backup.",
            "tags": "account,security,2fa,authentication"
        },
        {
            "title": "Test notification preferences",
            "steps": "1. Navigate to Account > Notifications\n2. Disable email notifications for campaign results\n3. Disable weekly report emails\n4. Enable Slack notifications (if integrated)\n5. Save preferences\n6. Trigger a campaign result event\n7. Verify email is NOT sent but Slack notification IS received",
            "expected": "Notification preferences respected. Disabled channels don't send. Enabled channels deliver correctly.",
            "tags": "account,notifications,preferences,settings"
        },
        {
            "title": "Verify team member invitation workflow",
            "steps": "1. Navigate to Account > Team\n2. Click Invite Member\n3. Enter email: newmember@example.com\n4. Select role: Editor\n5. Send invitation\n6. Check invitation email received\n7. Accept invitation as new member\n8. Verify permissions applied",
            "expected": "Invitation email sent with correct link. New member joins with Editor role and permissions.",
            "tags": "account,team,invitation,permissions"
        },
    ],
    "User Management": [
        {
            "title": "Verify role-based access control for Admin role",
            "steps": "1. Log in as Admin user\n2. Verify access to all modules: Campaigns, Reports, Integrations, Account\n3. Create a new campaign\n4. Delete an existing campaign\n5. Modify account settings\n6. Add/remove team members\n7. Verify all operations succeed",
            "expected": "Admin has full access to all features including campaign CRUD, settings, and user management.",
            "tags": "user-management,roles,rbac,admin"
        },
        {
            "title": "Test role-based access for Viewer role",
            "steps": "1. Create a user with Viewer role\n2. Log in as Viewer\n3. Try to create a new campaign (should fail)\n4. Try to edit an existing campaign (should fail)\n5. Try to delete a campaign (should fail)\n6. Verify Reports are viewable\n7. Verify Account > Team is not accessible",
            "expected": "Viewer can read campaigns and reports. Create, edit, delete operations are blocked.",
            "tags": "user-management,roles,rbac,viewer"
        },
        {
            "title": "Validate API token management",
            "steps": "1. Navigate to Account > API Tokens\n2. Generate new API token\n3. Set token name: 'Production API'\n4. Set permissions: Read campaigns, Write campaigns\n5. Copy token value\n6. Use token to authenticate API calls\n7. Revoke token\n8. Verify revoked token is rejected",
            "expected": "API token generated with correct permissions. Authenticated calls succeed. Revoked tokens are rejected.",
            "tags": "user-management,api,tokens,security"
        },
        {
            "title": "Test user session management",
            "steps": "1. Log in to VWO from two different browsers\n2. Navigate to Account > Sessions\n3. Verify both sessions are listed\n4. Terminate one session from UI\n5. Verify terminated session is logged out\n6. Verify other session remains active",
            "expected": "All active sessions listed. Session termination logs out the target session immediately.",
            "tags": "user-management,sessions,security,logout"
        },
        {
            "title": "Verify SSO/SAML login integration",
            "steps": "1. Navigate to Account > SSO\n2. Configure SAML with identity provider\n3. Enter SSO URL and certificate\n4. Map email attribute\n5. Save configuration\n6. Log out and use SSO login\n7. Verify automatic user provisioning",
            "expected": "SSO login redirects to IdP. Authentication succeeds. User auto-provisioned with correct permissions.",
            "tags": "user-management,sso,saml,authentication"
        },
    ],
    "Billing": [
        {
            "title": "Verify plan upgrade flow from Starter to Growth",
            "steps": "1. Navigate to Account > Billing\n2. View current plan: Starter\n3. Click Upgrade to Growth\n4. Review pricing and features comparison\n5. Enter payment details\n6. Confirm upgrade\n7. Verify new plan features are unlocked",
            "expected": "Plan upgrades successfully. Growth features become available immediately. Billing reflects prorated amount.",
            "tags": "billing,plan,upgrade,payment"
        },
        {
            "title": "Test invoice generation and download",
            "steps": "1. Navigate to Account > Billing > Invoices\n2. View invoice list\n3. Select a past invoice\n4. Click Download PDF\n5. Verify invoice details: company name, amount, date, tax\n6. Check invoice email delivery",
            "expected": "Invoice PDF downloads with correct details. Email copy sent to billing contact.",
            "tags": "billing,invoice,download,pdf"
        },
        {
            "title": "Validate payment method management",
            "steps": "1. Navigate to Account > Billing > Payment Methods\n2. Add new credit card\n3. Enter card details\n4. Set as default payment method\n5. Remove old payment method\n6. Verify default card is used for next payment",
            "expected": "Multiple payment methods supported. Default method used for billing. Old methods can be removed safely.",
            "tags": "billing,payment,cards,management"
        },
        {
            "title": "Test downgrade restrictions and data retention",
            "steps": "1. Navigate to Account > Billing > Plan\n2. Attempt to downgrade from Pro to Starter\n3. Read downgrade warning about feature loss\n4. Confirm downgrade\n5. Verify Premium features are locked\n6. Check data retention policy applied\n7. Verify existing campaigns continue running",
            "expected": "Downgrade completes with warning. Premium features locked. Existing campaigns continue but new premium features unavailable.",
            "tags": "billing,downgrade,plan,retention"
        },
        {
            "title": "Verify usage-based billing calculations",
            "steps": "1. Navigate to Account > Billing > Usage\n2. Review current month usage\n3. Check monthly visitor count: {visitors}\n4. Check campaign count: {n}\n5. Verify overage charges (if applicable)\n6. Compare with billing forecast",
            "expected": "Usage metrics accurately reflect account activity. Overage charges (if any) calculated correctly.",
            "tags": "billing,usage,overage,calculations"
        },
    ],
    "API & Webhooks": [
        {
            "title": "Verify REST API authentication with API key",
            "steps": "1. Generate API key from Account > API Tokens\n2. Set header: Authorization: Token {api_key}\n3. Call GET /api/v1/accounts\n4. Verify response with valid key\n5. Call with invalid key (should fail with 401)\n6. Call without key (should fail with 401)",
            "expected": "Valid API key returns account data. Invalid/missing key returns 401 Unauthorized.",
            "tags": "api,authentication,auth,rest"
        },
        {
            "title": "Test campaign creation via API",
            "steps": "1. Prepare JSON payload for campaign creation\n2. Include: name, type, variations, goals\n3. Call POST /api/v1/campaigns\n4. Verify campaign is created\n5. Call GET /api/v1/campaigns/{{id}}\n6. Verify all fields match",
            "expected": "Campaign created via API with correct parameters. GET returns matching campaign data.",
            "tags": "api,campaign,creation,crud"
        },
        {
            "title": "Validate API pagination and filtering",
            "steps": "1. Ensure 50+ campaigns exist\n2. Call GET /api/v1/campaigns?limit=10&offset=0\n3. Verify 10 results and total count\n4. Call with offset=10\n5. Verify different set of results\n6. Apply filter: ?status=active\n7. Verify only active campaigns returned",
            "expected": "Pagination returns correct subset. Filtering returns only matching records. Total count accurate.",
            "tags": "api,pagination,filtering,rest"
        },
        {
            "title": "Test rate limiting on API endpoints",
            "steps": "1. Call GET /api/v1/campaigns rapidly\n2. Send 100 requests in 1 minute\n3. Check response for 429 status code\n4. Verify Retry-After header present\n5. Wait for rate limit window to reset\n6. Verify normal requests resume",
            "expected": "Rate limiting kicks in after threshold. 429 returned with Retry-After header. Requests resume after window.",
            "tags": "api,rate-limiting,throttling,security"
        },
        {
            "title": "Verify webhook delivery with retry mechanism",
            "steps": "1. Configure webhook endpoint (use webhook.site)\n2. Configure for campaign.conversion event\n3. Trigger 5 conversion events\n4. Check webhook.site receives 5 requests\n5. Make endpoint return 500 error\n6. Trigger new event\n7. Verify retry mechanism (3 retries with backoff)",
            "expected": "Webhook delivers events to endpoint. Failed deliveries retry 3 times with exponential backoff.",
            "tags": "api,webhook,delivery,retry"
        },
    ],
    "Audience Targeting": [
        {
            "title": "Verify geolocation-based audience targeting",
            "steps": "1. Create campaign with location targeting\n2. Include countries: US, UK, Canada\n3. Exclude: California\n4. Launch campaign\n5. Test from included locations\n6. Test from excluded location (CA)\n7. Test from non-included country (Germany)",
            "expected": "Campaign shows to US/UK/Canada users (except CA). Hidden from all other locations.",
            "tags": "targeting,geolocation,audience,countries"
        },
        {
            "title": "Test device and browser targeting",
            "steps": "1. Create campaign with device targeting\n2. Include: Desktop, Tablet\n3. Exclude: Mobile\n4. Specify browsers: Chrome, Firefox\n5. Launch campaign\n6. Test on Desktop Chrome (should see)\n7. Test on Mobile Safari (should not see)\n8. Test on Desktop Edge (should not see)",
            "expected": "Campaign visible on desktop/tablet Chrome and Firefox. Not visible on mobile or unsupported browsers.",
            "tags": "targeting,device,browser,responsive"
        },
        {
            "title": "Validate cookie-based targeting for returning visitors",
            "steps": "1. Create campaign targeting returning visitors\n2. Set condition: Number of visits > 1\n3. Set cookie duration: 90 days\n4. Launch campaign\n5. Visit as first-time user (should not see)\n6. Visit again as returning user (should see)\n7. Clear cookies and visit (should not see)",
            "expected": "First-time visitors excluded. Returning visitors with cookie see the campaign. Cookie clearance resets.",
            "tags": "targeting,cookie,returning-visitors,visits"
        },
        {
            "title": "Test IP-based exclusion rules",
            "steps": "1. Create campaign with IP exclusions\n2. Add IP range: 192.168.1.0/24\n3. Add specific IP: 10.0.0.1\n4. Launch campaign\n5. Test from excluded IP (should not see)\n6. Test from non-excluded IP (should see)\n7. Test from IP range boundary",
            "expected": "Users from excluded IPs/ranges cannot see campaign. Allowed IPs see the campaign normally.",
            "tags": "targeting,ip-exclusion,rules,network"
        },
        {
            "title": "Verify campaign-level vs. variation-level targeting",
            "steps": "1. Create campaign with {n} variations\n2. Set campaign-level targeting: All countries\n3. Set variation A targeting: US only\n4. Set variation B targeting: UK only\n5. Launch campaign\n6. Test from US (should see variation A)\n7. Test from UK (should see variation B)\n8. Test from other country (sees control)",
            "expected": "Variation-level targeting overrides campaign targeting. Users see appropriate variation for their segment.",
            "tags": "targeting,variation-level,campaign-level,nested"
        },
        {
            "title": "Test JavaScript-based custom targeting conditions",
            "steps": "1. Create campaign with custom JS targeting\n2. Add JS condition: window.userTier === 'premium'\n3. Add fallback for undefined variable\n4. Launch campaign\n5. Visit page with userTier = 'premium' (should see)\n6. Visit page with userTier = 'free' (should not see)\n7. Visit page without variable (uses fallback)",
            "expected": "Custom JS targeting evaluates correctly. Fallback handles undefined variables gracefully.",
            "tags": "targeting,javascript,custom,advanced"
        },
        {
            "title": "Validate campaign-level audience exclusion",
            "steps": "1. Create Segment A: Mobile Users\n2. Create Segment B: New Visitors\n3. Create campaign excluding Segment A AND Segment B\n4. Launch campaign\n5. Test mobile + new visitor (should not see)\n6. Test desktop + returning visitor (should see)\n7. Test mobile + returning visitor (should not see)",
            "expected": "Campaign excludes all users matching any excluded segment. Overlapping segments don't cause double-counting.",
            "tags": "targeting,exclusion,segments,audience"
        },
    ],
    "Personalization": [
        {
            "title": "Verify personalized content based on user behavior",
            "steps": "1. Create personalization campaign\n2. Set rule: If user viewed /pricing 3+ times\n3. Set action: Show '20% off Annual Plan' banner\n4. Launch campaign\n5. Visit /pricing fewer than 3 times (no banner)\n6. Visit /pricing 3 times\n7. Navigate to homepage (banner appears)",
            "expected": "Personalized banner triggers after threshold behavior. Banner appears on subsequent pages.",
            "tags": "personalization,behavioral,content,banner"
        },
        {
            "title": "Test dynamic text replacement rules",
            "steps": "1. Create dynamic text variation\n2. Set: Replace 'Sign Up' with 'Get Started Free'\n3. Set condition: Traffic source = Organic\n4. Launch on homepage\n5. Visit from organic search\n6. Visit from paid ad\n7. Verify text replacement only occurs for organic traffic",
            "expected": "Text replacement triggers correctly for organic traffic. Other traffic sources see original text.",
            "tags": "personalization,dynamic-text,replacement,targeting"
        },
        {
            "title": "Validate recommendation engine for products",
            "steps": "1. Enable product recommendations\n2. Configure recommendation type: 'Frequently Bought Together'\n3. Set placement: Product page below add-to-cart\n4. Set max recommendations: {n}\n5. Launch campaign\n6. Visit product page\n7. Verify recommendations are relevant\n8. Check recommendation count",
            "expected": "Product recommendations display {n} relevant products. Recommendations update based on browsing behavior.",
            "tags": "personalization,recommendations,products,ecommerce"
        },
        {
            "title": "Test geo-personalization with localized content",
            "steps": "1. Create geo-personalization campaign\n2. Set rule: Country = France -> Show French content\n3. Set rule: Country = Germany -> Show German content\n4. Default: Show English content\n5. Launch campaign\n6. Test with French IP\n7. Test with German IP\n8. Test with Spanish IP",
            "expected": "Users see content in their local language. Default content shows for unconfigured locations.",
            "tags": "personalization,geo,localization,i18n"
        },
        {
            "title": "Verify time-based personalization rules",
            "steps": "1. Create time-based personalization\n2. Rule: Monday-Friday 8AM-10AM -> Show 'Morning Coffee' offer\n3. Rule: Friday 5PM-8PM -> Show 'Weekend Special' offer\n4. Default: Show standard offer\n5. Launch campaign\n6. Test at Wednesday 9AM\n7. Test at Friday 6PM\n8. Test at Saturday 2PM",
            "expected": "Correct offer displays based on day and time. Default shows when no rule matches.",
            "tags": "personalization,time-based,schedule,offers"
        },
    ],
}

COLORS = {
    "Campaign Management": "#4A90D9",
    "User Segmentation": "#7B61FF",
    "Reporting & Analytics": "#2ECC71",
    "Integrations": "#E67E22",
    "Account Settings": "#E74C3C",
    "User Management": "#1ABC9C",
    "Billing": "#F39C12",
    "API & Webhooks": "#9B59B6",
    "Audience Targeting": "#3498DB",
    "Personalization": "#FF6B6B",
}

PRIORITIES = ["P0", "P1", "P2", "P3"]


def generate_test_cases(count: int = 5000) -> List[Dict]:
    cases = []
    templates_pool = []
    for module, templates in TEMPLATES.items():
        for t in templates:
            templates_pool.append((module, t))

    for i in range(1, count + 1):
        module, t = random.choice(templates_pool)
        n = random.randint(2, 5)
        traffic = random.randint(10, 100)
        conversions = random.randint(1, 50)
        conversions2 = conversions + random.randint(-10, 20)
        revenue = random.randint(10, 200)
        total_revenue = revenue * n
        api_key = "vwo_" + "".join(random.choices("abcdef0123456789", k=32))
        visitors = random.randint(500, 5000)
        days = random.randint(3, 30)

        title = t["title"].format(n=n, traffic=traffic, conversions=conversions,
                                  conversions2=conversions2, revenue=revenue,
                                  visitors=visitors, days=days, total_revenue=total_revenue,
                                  api_key=api_key)
        steps = t["steps"].format(n=n, traffic=traffic, conversions=conversions,
                                  conversions2=conversions2, revenue=revenue,
                                  visitors=visitors, days=days, total_revenue=total_revenue,
                                  api_key=api_key)
        expected = t["expected"].format(n=n, traffic=traffic, conversions=conversions,
                                        conversions2=conversions2, revenue=revenue,
                                        visitors=visitors, days=days, total_revenue=total_revenue,
                                        api_key=api_key)
        tags = t["tags"]

        jira_id = f"VWO-{1000 + i}"
        priority = random.choice(PRIORITIES)

        cases.append({
            "id": i,
            "jira_id": jira_id,
            "title": title,
            "steps": steps,
            "expected": expected,
            "priority": priority,
            "module": module,
            "tags": tags,
            "preconditions": "User is logged in to VWO account with appropriate permissions." if "account" not in module.lower() and "billing" not in module.lower() else "Active VWO account with valid subscription.",
            "created_by": random.choice(["John Smith", "Sarah Johnson", "Mike Chen", "Emily Brown", "Alex Kumar"]),
            "status": random.choice(["Active", "Active", "Active", "Draft", "Deprecated"]),
        })

    return cases


def write_csv(cases: List[Dict], filepath: str):
    fieldnames = ["id", "jira_id", "title", "steps", "expected", "priority",
                  "module", "tags", "preconditions", "created_by", "status"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cases)
    print(f"[OK] Wrote {len(cases)} test cases to {filepath}")


if __name__ == "__main__":
    testcase_dir = os.path.join(os.path.dirname(__file__), "testcase")
    os.makedirs(testcase_dir, exist_ok=True)
    filepath = os.path.join(testcase_dir, "vwo_test_cases.csv")
    cases = generate_test_cases(5000)
    write_csv(cases, filepath)
