# SMS Implementation - Visual Guide

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     ADMIN INTERFACE                             │
│              (Manage Tasks Dashboard)                           │
│                                                                 │
│  Task #42  | Customer: Maria  | Status: COMPLETED              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ View | Edit | [APPROVE BUTTON ✓]                        │   │
│  └─────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │   Django Backend                     │
        │   (views.approve_task)               │
        │                                      │
        │  1. Approve task                     │
        │  2. Create commission                │
        │  3. Trigger SMS Service              │
        └──────────────┬───────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────┐
        │   SMS Service                        │
        │   (sms_service.py)                   │
        │                                      │
        │  • Get customer name & phone         │
        │  • Build SMS message                 │
        │  • Call Semaphore API                │
        │  • Log result                        │
        └──────────────┬───────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────┐
        │   Semaphore SMS API                  │
        │   https://semaphore.co/api/v4/...    │
        │                                      │
        │   Sends to: 09998887777              │
        └──────────────┬───────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────┐
        │   Customer Mobile Phone              │
        │                                      │
        │   SMS Received:                      │
        │   "Hi Maria, your garment for       │
        │    Order #42 is ready for pickup     │
        │    at El Senior Dumingag. Thank you!"│
        └──────────────────────────────────────┘
```

## Data Flow

```
TASK APPROVAL SEQUENCE:

┌─────────────────┐
│ Admin clicks    │
│ APPROVE button  │
└────────┬────────┘
         │
         ▼
    ┌────────────────────────────────────┐
    │ API Request:                       │
    │ POST /api/admin/tasks/42/approve/  │
    └────────┬─────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────┐
    │ approve_task() function:           │
    │ ✓ Find task                        │
    │ ✓ Check status is COMPLETED        │
    │ ✓ Call OrderManager.approve_task() │
    └────────┬─────────────────────────┘
             │
             ├─────────────────┐
             │                 │
             ▼                 ▼
    ┌─────────────────┐  ┌──────────────────────┐
    │ Create          │  │ SMS Notification     │
    │ Commission      │  │ (Non-blocking)       │
    │ ✓ Success       │  │ Try:                 │
    │                 │  │  • Get customer      │
    │                 │  │  • Send SMS          │
    │                 │  │ Catch:               │
    │                 │  │  • Log error         │
    │                 │  │  • Continue anyway   │
    └────────┬────────┘  └──────────┬───────────┘
             │                      │
             └──────────┬───────────┘
                        │
                        ▼
            ┌──────────────────────────┐
            │ Return Success Response:  │
            │ "Task approved!           │
            │  Commission: ₱500         │
            │  Customer notified via    │
            │  SMS"                     │
            └──────────────────────────┘
```

## Setup Flow

```
START
  │
  ├─[Get API Key]──────────────────┐
  │                                 │
  │  1. Visit semaphore.co          │
  │  2. Sign up (free)              │
  │  3. Get API key                 │
  │                                 │
  └─────────┬──────────────────────┘
            │
            ▼
  ├─[Set Environment]──────────────┐
  │                                 │
  │  export SEMAPHORE_API_KEY=...   │
  │                                 │
  └─────────┬──────────────────────┘
            │
            ▼
  ├─[Test SMS]──────────────────────┐
  │                                 │
  │  python manage.py test_sms ...  │
  │                                 │
  │  ✓ If success → DONE            │
  │  ✗ If error → Debug             │
  │                                 │
  └─────────┬──────────────────────┘
            │
            ▼
  ├─[Use System]───────────────────┐
  │                                │
  │  1. Go to Manage Tasks         │
  │  2. Approve a task             │
  │  3. SMS sent automatically    │
  │                                │
  └─────────┬──────────────────────┘
            │
            ▼
          DONE ✓
```

## Error Handling Flow

```
SMS Operation Started
        │
        ▼
    ┌──────────────────┐
    │ Has API Key?     │
    └─────┬────┬───────┘
          │ No │
          │    └─→ Log Error
          │        Continue
    ┌─────┘        Anyway
    │ Yes
    │
    ├─► ┌──────────────────┐
    │   │ Has Phone Number?│
    │   └─────┬────┬───────┘
    │         │ No │
    │         │    └─→ Log Error
    │         │        Continue
    │   ┌─────┘
    │   │ Yes
    │   │
    │   ├─► ┌──────────────────┐
    │       │ Send to API      │
    │       └─────┬────┬───────┘
    │             │ OK │
    │             │    │
    │             │    └─► ┌──────────────┐
    │             │        │ Log Success  │
    │             │        │ Continue     │
    │             │        └──────────────┘
    │             │
    │             │ ERROR
    │             │
    │             └──→ ┌──────────────┐
    │                 │ Log Error     │
    │                 │ Continue      │
    │                 │ Anyway        │
    │                 └──────────────┘
    │
    └────────┬───────────────────────┐
             │                       │
             ▼                       ▼
    ┌──────────────┐        ┌──────────────┐
    │Task Approved │        │Task Approved │
    │SMS Sent OK   │        │SMS Failed    │
    │✓ Success ✓   │        │✓ Still OK ✓  │
    └──────────────┘        └──────────────┘
```

## Component Interaction

```
                        manage_tasks.html
                                │
                                │ User clicks approve
                                ▼
                        ┌─────────────────┐
                        │  AJAX Request   │
                        │  POST /api/.../ │
                        └────────┬────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                        │
                    ▼                        ▼
        ┌─────────────────────┐    ┌──────────────────┐
        │   views.py          │    │  models.py       │
        │ approve_task()      │◄──►│ Task, Order,     │
        │                     │    │ Customer         │
        └────────┬────────────┘    └──────────────────┘
                 │
                 ├─ Task validation
                 ├─ Commission creation
                 │
                 ▼
        ┌─────────────────────┐
        │  sms_service.py     │
        │  SemaphoreSMS       │
        └────────┬────────────┘
                 │
                 ├─ Get customer info
                 ├─ Build message
                 ├─ Prepare API request
                 │
                 ▼
        ┌─────────────────────┐
        │  requests library   │
        │  HTTP/HTTPS POST    │
        └────────┬────────────┘
                 │
                 ▼
        ┌─────────────────────┐
        │  Semaphore API      │
        │  SMS Gateway        │
        └──────────────────────┘
```

## Decision Tree

```
                    ┌─ Is API Key Set? ──N──► ERROR: Not configured
                    │                         LOG & SKIP SMS
                    Y
                    │
                    ├─ Is Phone Number? ──N──► ERROR: No phone
                    │                         LOG & SKIP SMS
                    Y
                    │
                    ├─ API Request ──┐
                    │               │
                    │        ┌──────┴─────┐
                    │        │            │
                    Y        N         TIMEOUT
                    │        │            │
              SUCCESS      ERROR        ERROR
                    │        │            │
                    └─ LOG ─►└────┬───────┘
                                  │
                                  ▼
                            Task Still Approves
                            Response Sent
                            Admin Notified
```

## Message Flow Example

```
ADMIN APPROVAL:
├─ Approve Task #42
│  └─ Customer: Maria Santos
│     Phone: 09998887777
│     Order: #42
│     Garment: Blouse
│
SMS MESSAGE GENERATED:
├─ Template: "Hi {name}, your garment for Order #{id} is ready..."
├─ Substitution: name = "Maria", id = "42"
│
SMS CONTENT:
├─ "Hi Maria Santos, your garment for Order #42 is ready for pickup"
│  "at El Senior Dumingag. Thank you!"
│
SMS DELIVERY:
├─ Provider: Semaphore API
├─ Recipient: 09998887777
├─ Sender: StitchFlow
├─ Status: Delivered
│
RESPONSE TO ADMIN:
├─ "Task approved!"
├─ "Commission: ₱500.00"
└─ "Customer notified via SMS ✓"
```

## Configuration Layout

```
┌─────────────────────────────────────┐
│  Django Settings (settings.py)      │
├─────────────────────────────────────┤
│  SEMAPHORE_API_KEY                  │
│  ├─ Source: Environment Variable    │
│  │  (SEMAPHORE_API_KEY=...)         │
│  │                                  │
│  ├─ Fallback: 'your-api-key-here'  │
│  │  (Development placeholder)       │
│  │                                  │
│  └─ Usage: sms_service.py           │
│                                     │
│  SEMAPHORE_SENDER_NAME              │
│  ├─ Value: 'StitchFlow'             │
│  ├─ Purpose: SMS sender name        │
│  └─ Customizable: Yes               │
└─────────────────────────────────────┘
```

## File Interaction Diagram

```
         ┌─────────────────────────┐
         │  Browser / Admin User   │
         └────────────┬────────────┘
                      │
              Templates:
              manage_tasks.html
                      │
                      ├─ JavaScript handlers
                      ├─ AJAX requests
                      └─ UI updates
                      │
                      ▼
         ┌─────────────────────────┐
         │  Django Backend         │
         │  (views.py)             │
         │  approve_task()         │
         └────────────┬────────────┘
                      │
           ┌──────────┼──────────┐
           │          │          │
       Business    Models    SMS Service
       Logic       (models.py)  (sms_service.py)
    (business_      │          │
     logic.py)      │          ├─ Configuration
                    │          │  (settings.py)
        ┌───────────┘          │
        │                      ├─ HTTP Library
        │                      │  (requests)
        ▼                      │
      ┌──────────┐            ▼
      │Database  │        ┌──────────┐
      │ SQLite   │        │ Semaphore│
      │          │        │API       │
      │Tasks     │        │          │
      │Orders    │        │SMS       │
      │Customers │        │Gateway   │
      └──────────┘        └──────────┘
```

## Testing Flow

```
UNIT TEST:
┌─────────────────────┐
│ Management Command  │
│ test_sms            │
└────────┬────────────┘
         │
         ├─ Input: Phone number
         ├─ Input: Customer name (optional)
         ├─ Input: Order ID (optional)
         │
         ▼
    ┌─────────────────┐
    │ Call SMS Service│
    │ directly        │
    └────────┬────────┘
             │
             ├─ SUCCESS: Show ✓ message
             └─ FAILURE: Show ✗ message


END-TO-END TEST:
┌─────────────────────┐
│ 1. Create Task      │
│ 2. Complete Task    │
│ 3. Approve Task     │
└────────┬────────────┘
         │
         ▼
    ┌─────────────────┐
    │ SMS Auto-Sent   │
    └────────┬────────┘
             │
             ├─ Check: UI shows SMS message
             ├─ Check: Customer receives SMS
             └─ Check: Logs show success
```

## Status Indicators

```
✓ Configuration Complete
├─ SEMAPHORE_API_KEY set
├─ requirements.txt updated
└─ settings.py configured

✓ Code Integration Complete
├─ sms_service.py created
├─ views.py updated
├─ manage_tasks.html updated
└─ test_sms.py created

✓ Documentation Complete
├─ README_SMS.md
├─ SMS_QUICKSTART.md
├─ SMS_IMPLEMENTATION.md
├─ SMS_TESTING_GUIDE.md
└─ SMS_INTEGRATION_SUMMARY.md

✓ Ready for Deployment
├─ All components integrated
├─ Error handling complete
├─ Logging configured
└─ Testing possible
```

## Summary Flowchart

```
                    START
                      │
                      ▼
            Get Semaphore API Key
                      │
                      ▼
         Set Environment Variable
                      │
                      ▼
          Run: python manage.py test_sms
                      │
                    ┌─┴─┐
                    │ OK│
                    Y  N
                    │  │
                    │  ├─► DEBUG
                    │  │    └─► FIX
                    │  │        └─► RETRY
                    │  │
                    ▼  ▼
              DEPLOY / USE
                      │
                      ▼
           Go to Manage Tasks
                      │
                      ▼
            Click Approve Button
                      │
                      ▼
         SMS Sent to Customer
                      │
                      ▼
              SUCCESS! ✓✓✓
```

---

This visual guide shows how all components work together.

For detailed steps, see **SMS_QUICKSTART.md** →
