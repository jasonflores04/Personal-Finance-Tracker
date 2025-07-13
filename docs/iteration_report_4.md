Iteration Report 4
===
---

### Group members and their jobs:
- Froylan: 
  - Add functionality for the Savings page
  - Update budget page
- Kyle:
  - Fixing Unit Testing
  - Bulma Design for Settings page
- Tom:
  - Develop admin mask functionality
- Nazar:
  - Add functionality for editing an expense
- Jason:
  - Additional functionality for Reports page
  - Updating income to work with balance


---
### Work Completed:
- Froylan:
  - Full functionality for Savings page
  - Full functionality for Budget page
  - Linking budget and expenses to show unaccounted expense categories
  - Edit/delete functionality for Savings page
  - Delete functionality for Budget page
- Kyle:
  - Fixed Unit Tests
  - Setup styles for Settings page
- Tom:
  - Functionality of the admin mask
- Nazar:
  - Created edit feature for expenses
  - Fixed bug where all user data would show, now only shows current user
  - Expenses and Subscriptions now work with balance
  - Auto-fill for current date if no given value in expenses/subscriptions
  - Input amount for expenses now only takes positive floats/ints
  - Date restriction for expenses/subscriptions
- Jason:
  - Changed income filters to go by user_id
  - Updating balance with income
  - Input validation for amount added and dates

---
### Work planned, but not finished:
- Exporting reports

---
### Roadblocks:
- Meetings:
  - Conflicts with finding a meeting time that works for everyone is ongoing.

--- 
### Adjustments:
- Design and layout still need minor discussion
- Focusing on getting tasks completed when there are outside dependencies based on a task

---
### Helpful tool:
- Continue - Useful for getting initial ideas on completing a task

---
### One thing we learned:
- If a task has dependencies on other tasks, we need to complete the dependency tasks earlier in the week to have more time overall. 

------

# Iteration Plan 5

## User Stories Week 5

### User - Tracking Budget over time - Froylan
As a user, I want the ability to see my budget in comparison to my income and expenses over a given timeframe.
- Add handling for time in the same format as income and expenses
- Add a time category for budget categories

### User - Reports - Jason
As a user, I want the ability to generate reports so that I can view my spending habits in a new and different way.
- Reports exported (e.g. PDF)

### User - Layout - Kyle
As a user, I want a simple layout that makes navigating the application more convenient.
- Reformat the settings page
- Create a more consistent layout for all pages

### Admin/Unit Testing - Tom
As an Admin, I want more detailed tests in place to cover every aspect of the application.
- Add testing to cover all edit/delete functions
- Add testing to cover navigation of multiple pages in a single test

### User - Bills/Subscriptions - Nazar
As a user, I want the ability to schedule bills and subscriptions so that I can see how much money I will spend on these at the beginning of the month.
- Adding ability to enter amount and date to add expense on that day in the future
- Adding the ability to handle subscriptions


-------
# Iteration Plan 6

- Fix any present bugs
- Cover all aspects of application in unit testing
- Finishing formatting across all pages