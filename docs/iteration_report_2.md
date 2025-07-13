Iteration Report 2
===
---
### Group Members and their jobs:
- Froylan:
  - Work on Budgets Backend
  - (midweek) Add additional routes to budget
  - (midweek) fix file names
- Kyle:
  - Continue to work on settings feature
  - (midweek) Split method routes for login and register
  - (midweek) Update password hashing to fit Mark's specs
- Tom:
  - Finish Homepage front-end and start backend
  - Hide navbar and footer in login and register
  - (midweek) update schema
- Nazar:
  - Expenses base functionality
  - (midweek) fix flash message error on expenses
  - (midweek) fix route/request methods for expenses
  - (midweek) Add charts
- Jason:
  - Income base functionality
  - (midweek) Add income date's
  - (midweek) Fix income flash messages
  - (midweek) split method routes for income
---
### Work Completed:
- Froylan:
  - Budgets base functionality
  - Added additional routes to budget
  - fixed file names (most of them)
- Kyle:
  - Split method routes for login and register
  - Updated password hashing to fit Mark's specs
- Tom:
  - Finished Homepage front-end and started backend
  - Hid navbar and footer in login and register
  - updated Schema
- Nazar:
  - Expenses Base Functionality
  - fixed flash message error on expenses
  - fixed route/request methods for expenses
  - Added charts
- Jason:
  - Income Base Functionality
  - Added income date's
  - Fixed income flash messages
  - split method routes for income

---
### Work Planned, but not finished:
- Income and Expenses do not update users balance, small bug we forgot to implement
- Homepage and Budget missing some functionality

---
### Roadblocks:
- Meetings.
  - Thursday meeting only attended by Tom and Kyle, but still productive
  - Friday meeting missing Kyle, but Tom had notes from prior meeting and shared thoughts with rest of group
  - To fix this we discuss in class thursday if we meet thursday and always meet friday

- Commits:
  - Froylan pushed to main and didn't have a branch, no major issues however

---
### Adjustments:
- We decided to work on charts instead of subscriptions as planned
- We were ahead of our plan so we decided to dedicate time to iron out bugs and make some tweaks to the design and adding functionality we may have missed.
- We also plan to change our Admin feature to allow admins to see the site as another user
- We are also adding edit and delete functions for features as our admin feature is no longer containing this exclusive feature

---
### Helpful tools:
- stack overflow (website)
- Bulma Documentation (website)
- Continue

---
### One thing we learned:
- Always update and reinitialize your database after changes are made
- Don't push to main, use a branch
----------

# Iteration Plan 3

### Finish/Last Week
- Tom: Homepage Backend
- Froylan: Budget
- Kyle: Settings
- Nazar: Delete
- Jason: Edit

## User Stories Week 3

### User - Reports - Jason
As a user, I want the ability to generate reports so that I can view my spending habits in a new and different way. 
- Start implementing reports generation feature
- Reports exported (e.g. PDF)

### User - Charts - Nazar (completed Already was planned)
As a user, I want to show interactive charts and graphs so that I can see my spending and savings habits over time.
- Add charts for income/expenses and savings goals

### User - Bills/Subscriptions - Nazar (after expenses complete with delete and edit)
As a user, I want the ability to schedule bills and subscriptions so that I can see how much money I will spend on these at the beginning of the month.
- Add scheduling functionality and make sure upcoming payments are shown

### Admin/Creator Accounts - Kyle
As an Admin, I want an admin account such that when I log in I am an Admin
- Develop admin login functionality

### Admin/Creator Mask - Tom
As an Admin, I want a select menu where I can choose to see and view the site as another user
- Develop admin mask functionality

### User - Saving Goals - Froylan (after budget is finished)
As a user, I want to be able to set savings goals so that I can see close I am to those goals.
- Start implementing the Saving goals feature
- Add functionality to track progress toward goals

### User - Edit - Jason
As a user, I want to be able to edit my income, and expenses
- add feature to income and port to other features

### User - Delete - Nazar
As a user, I want to delete my income, and expense statements
- Add to expenses and then port to other features