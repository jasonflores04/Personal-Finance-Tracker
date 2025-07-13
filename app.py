# -*- coding: utf-8 -*-
"""
    Trackr Plus Plus
    ~~~~~~
"""

import os
from fileinput import filename

from select import select
from sqlite3 import dbapi2 as sqlite3

import click
from dateutil.utils import today
from flask import Flask, request, g, redirect, url_for, render_template, flash, session, make_response
from werkzeug.security import check_password_hash, generate_password_hash

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta

from datetime import datetime
import calendar

from xhtml2pdf import pisa
from io import BytesIO


# create our little application :)
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'trackr.db'),
    SECRET_KEY='development key',
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('admin')
@click.argument('username')
@click.argument('password')
def add_admin(username, password):
    db = get_db()
    db.cursor().execute('INSERT INTO users (admin, username, password, balance) VALUES (?, ?, ?, ?)', (1, username, generate_password_hash(password), 0))
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()



@app.route('/login', methods=['GET'])
def login_page():
    """
    This is the login page for the tracker plus plus program.
    """
    #if this is a get method, just render the page.
    return render_template('login.html')

@app.route('/login_account', methods=['POST'])
def login_account():
    # if this is a post method, and has a username and password check to see if they are valid
    username = request.form['username']
    password = request.form['password']
    db = get_db()
    error = None
    user = db.execute(
        'SELECT * FROM users WHERE username = ?', [username]
    ).fetchone()

    if user is None:
        error = 'Incorrect username.'
    elif not check_password_hash(user['password'], password):
        error = 'Incorrect password.'

    if error is None:
        session.clear()
        session['user_id'] = user['id']
        session['real_id'] = user['id']
        session['loggedin'] = True
        session['username'] = username
        return redirect(url_for('home_page'))

    flash(error)
    return redirect(url_for('login_page'))


@app.route('/register', methods=['GET'])
def register_page():
    """
    this will register an account in the db
    """

    # if the request is a get request, render the page
    return render_template('register.html')

@app.route('/register_account', methods=['POST'])
def register_account():
    # otherwise try to register an account
    username = request.form['username']
    if username == '' or request.form['password'] == '':
        flash('Please enter a username and password')
        return redirect(url_for('register_page'))
    db = get_db()
    cur = db.execute('select * from users where username = ?',
                     [username])
    # if account exists with this username, flash a message and redirect to this url
    account = cur.fetchone()
    if account:
        flash("username already exists")
        return redirect(url_for('register_page'))

    password = request.form['password']


    # add user to db and go to login page
    db.execute('insert into users (username, password) values (?, ?)',
               [username, generate_password_hash(password)])
    db.commit()
    # session['loggedin'] = False
    return redirect(url_for('login_page'))


@app.route('/logout', methods=['GET'])
def logout():
    """
    this will log the user out and redirect to the login page
    """
    user_id = session.get('id')

    # deletes graph of chosen category for the user
    months_graph_path = os.path.join('static', f'months_graph_{user_id}.svg')
    if os.path.exists(months_graph_path):
        os.remove(months_graph_path)

    session.clear()
    return redirect(url_for('login_page'))


@app.route('/', methods=['GET'])
def home_page():

    # login check
    if not session.get('loggedin'):
        return redirect(url_for('login_page'))
    else:
        # get the period and calculate offset
        time_bound = request.args.get('time')
        if time_bound == "Past Week":
            time_offset = "-7 days"
        elif time_bound == "Past Month":
            time_offset = "-1 month"
        elif time_bound == "Past 3 Months":
            time_offset = "-3 months"
        elif time_bound == "Past 6 Months":
            time_offset = "-6 months"
        elif time_bound == "Past Year":
            time_offset = "-1 year"
        elif time_bound == "All Past":
            time_offset = "-100 years"
        else:
            time_offset = "-1 month"  # default is 1 month
            time_bound = "Past Month"

        db = get_db()

        current_year = datetime.now().year # get current year as int

        # Create Expenses DataFrame with only amount and date
        df_expenses = pd.read_sql("SELECT amount, date FROM expenses where user_id = (?)", db,
                         params=[session.get('user_id')])  # create a dataframe object

        df_expenses.loc[:, 'months'] = df_expenses.loc[:, 'date'].str[5:7] # create new column 'months'
        df_expenses = df_expenses[df_expenses.loc[:, 'date'].str[0:4] == str(current_year)] # get rows only for current year
        df_expenses = df_expenses.drop(columns=['date']) # remove date column
        df_exp_grouped = df_expenses.groupby(by='months').sum() # group by months and get expenses' sum for each month
        df_exp_grouped = df_exp_grouped.fillna(0) # replace NaN values with zeros
        df_exp_grouped = df_exp_grouped.astype('float') # convert type to float

        # Create Income DataFrame with only amount and date
        df_income = pd.read_sql("SELECT amount, date FROM income where user_id = (?)", db,
                                  params=[session.get('user_id')])  # create a dataframe object

        df_income.loc[:, 'months'] = df_income.loc[:, 'date'].str[5:7]
        df_income = df_income[df_income.loc[:, 'date'].str[0:4] == str(current_year)] # get rows only for current year
        df_income = df_income.drop(columns=['date']) # remove date column
        df_inc_grouped = df_income.groupby(by='months').sum() # group by months and get expenses' sum for each month
        df_inc_grouped = df_inc_grouped.fillna(0) # replace NaN values with zeros
        df_inc_grouped = df_inc_grouped.astype('float')  # convert type to float

        df_bal = df_inc_grouped.sub(df_exp_grouped, fill_value=0).fillna(0) # calculate balance and replace NaN values with zeros
        df_bal = df_bal.reset_index() # reset index

        fig, ax = plt.subplots() # create a figure and a set of subplots

        sns.lineplot(x='months', y='amount', data=df_bal.sort_values(by='months'),
                     color="black", ax=ax) # draws line graph

        # Create red and green dots based on the balance
        for i in range(len(df_bal)):
            # set red dots if balance is negative
            if df_bal['amount'][i] < 0:
                ax.plot(df_bal['months'][i], df_bal['amount'][i], 'ro')
            # set green dots if balance is positive
            else:
                ax.plot(df_bal['months'][i], df_bal['amount'][i], 'go')

        balancelineplot_path = os.path.join('static', 'balancelineplot.svg')  # path to save the generated graph file

        # Customization of axes and title
        plt.title(f"Monthly Net Income for {current_year}", weight="bold")
        plt.xlabel("Months", weight="bold")
        plt.ylabel("Amount ($)", weight="bold")

        plt.savefig(balancelineplot_path, format='svg')  # saves a generated plot as an .svg file in "static/" folder
        plt.close()

        # Get User info
        cur = db.execute('SELECT username, balance, savings_name FROM users WHERE id = ?',
                         [session.get('user_id')])
        user_info = cur.fetchone()
        bal = user_info[1]

        # get savings goal, set to 0.0 if null
        cur = db.execute('SELECT coalesce(savings_goal, 0.0) FROM users WHERE id = ?',
                         [session.get('user_id')])
        savings_goal_row = cur.fetchone()
        savings_goal = round(savings_goal_row[0],2)

        # get Income for specified period
        cur = db.execute('SELECT coalesce(sum(amount), 0.0) FROM income WHERE user_id = ? and income.date > date("now", ?) and income.date < date("now", "1 days")',
                         [session.get('user_id'), time_offset])
        income_row = cur.fetchone()
        income_sum = round(income_row[0], 2)

        # get Expenses for specified period
        cur = db.execute('SELECT Coalesce(SUM(amount), 0.0) FROM expenses WHERE user_id = ?and expenses.date > date("now", ?) and expenses.date < date("now", "1 days")',
                         [session.get('user_id'), time_offset])
        expenses_row = cur.fetchone()
        expense_sum = round(expenses_row[0], 2)

        net_income = round(income_sum - expense_sum, 2)

        # Income to Expense Ratio
        ratio = income_to_expense_ratio(income_sum, expense_sum)
        inc_to_exp_inc = ratio[0]
        inc_to_exp_exp = ratio[1]

        # Balance to Exp ratio
        bal_t_e_e = 1
        if expense_sum == 0.0:
            bal_t_e_b = bal
        else:
            bal_t_e_b = round((bal / expense_sum), 2)

        # Average Income and expenses per month (mostly done using continue)
        avg_inc = month_avg("income", session.get('user_id'))
        avg_exp = month_avg("expenses", session.get('user_id'))

        # get the total savings so far, 0.0 if none
        cur = db.execute('SELECT coalesce(SUM(amount), 0.0) FROM savings WHERE user_id = ?',
                         [session.get('user_id')])
        savings_total_row = cur.fetchone()
        savings_total = round(savings_total_row[0],2)

        if savings_goal == 0.0:
            s_percent = 0
        else:
            s_percent = round(round(savings_total/savings_goal, 4) * 100, 2)

        month = datetime.now().month
        budget_query = """SELECT b.category, b.amount AS budget_amount, COALESCE(e.total_expense, 0.0) AS expense_amount FROM budget b LEFT JOIN (SELECT category, SUM(amount) AS total_expense FROM expenses WHERE user_id = ? AND CAST(STRFTIME("%m", date) AS INTEGER) = ? GROUP BY category) e ON b.category = e.category WHERE b.user_id = ? AND b.month = ?"""

        budget = db.execute(budget_query,
                            [session.get('user_id'), month, session.get('user_id'), month]).fetchall()

        return render_template('homepage.html', user_info=user_info, income=income_sum, expenses=expense_sum, net_income=net_income, time_bound=time_bound,
                               inc_to_exp_inc=inc_to_exp_inc, inc_to_exp_exp=inc_to_exp_exp, bal_t_e_b=bal_t_e_b,bal_t_e_e=bal_t_e_e, avg_inc=avg_inc, avg_exp=avg_exp,
                               savings_goal=savings_goal, savings_total=savings_total, s_percent=s_percent, budget=budget,homepage_graph = url_for('static', filename='balancelineplot.svg'))

"""
Helper function that given strings of time period start and end and amount returns the average amount per month
"""
def month_avg_calc(first_date_str, last_date_str, amount):
    # Convert the date strings to datetime objects
    first_date = parser.parse(first_date_str).date()
    last_date = parser.parse(last_date_str).date()

    # Calculate the difference in months
    date_difference = relativedelta(last_date, first_date)
    months_difference = (date_difference.years * 12 + date_difference.months) + 1
    avg = round(amount / months_difference, 2)
    return avg

"""
Given the table name and user_id finds the monthly average of the table's amount
"""
def month_avg(db_name, user_id):
    db = get_db()
    today = datetime.now().strftime("%Y-%m-%d")
    # Average Expenses per month (ported from avg_income)
    cur = db.execute('SELECT Coalesce(SUM(amount), 0.0) FROM {0} WHERE user_id = ? and {0}.date < date("now", "1 days")'.format(db_name),
        [user_id])
    to_now_row = cur.fetchone()
    to_now_sum = to_now_row[0]

    cur = db.execute('SELECT date from {0} where user_id = ? order by date asc limit 1'.format(db_name),
                     [user_id])
    first_date_row = cur.fetchone()
    if first_date_row:
        first_date_str = first_date_row[0]
    else:
        first_date_str = today

    cur = db.execute('SELECT date from {0} where user_id = ? and {0}.date < date("now", "1 days") order by date desc limit 1'.format(db_name),
        [user_id])
    last_date_row = cur.fetchone()
    if last_date_row:
        last_date_str = last_date_row[0]
    else:
        last_date_str = today

    avg = month_avg_calc(first_date_str, last_date_str, to_now_sum)
    return avg

"""
Given an income and expense returns the ratio in a list
"""
def income_to_expense_ratio(income, expenses):
    if income == expenses:
        return [1,1]
    if income == 0.0:
        return [1, expenses]
    elif expenses == 0.0:
        return [income, 1]
    elif income > expenses:
        return [round(income/expenses, 4), 1]
    elif income < expenses:
        return [1, round(expenses/income, 2)]

@app.route('/income', methods=['GET'])
def show_income():
    """
    Function that displays income records, categories, and totals
    """
    db = get_db()
    # If category is requested then filter the records by the category selected by the user
    if request.args.get('category'):
        cur = db.execute('SELECT id, amount, category, description, date FROM income WHERE user_id = ? AND category = ? ORDER BY date DESC',
                         [session.get('user_id'), request.args.get('category')])
    # If not, retrieve every single record
    else:
        cur = db.execute('SELECT id, amount, category, description, date FROM income WHERE user_id = ? ORDER BY date DESC',
                         [session.get('user_id')])
    entries = cur.fetchall()

    # Retrieve distinct categories to use them in the income form
    cur = db.execute('SELECT DISTINCT category FROM income WHERE user_id = ?',
                     [session.get('user_id')])
    categories = [category['category'] for category in cur.fetchall()]

    # Calculate total income by using 'SUM' and summing all amounts given in the income table
    cur = db.execute('SELECT SUM(amount) as total_income FROM income WHERE user_id = ?',
                     [session.get('user_id')])

    total_income = cur.fetchone()['total_income'] or 0  # Avoid the display of 'None' in the website by putting 0 if there is no record given by the user

    # Calculate total income per category by grouping 'category' records
    cur = db.execute('SELECT category, SUM(amount) as total_per_category FROM income WHERE user_id = ? GROUP BY category',
                     [session.get('user_id')])
    income_per_category = cur.fetchall()

    return render_template('income.html', entries=entries, categories=categories, total_income=total_income, income_per_category=income_per_category)


@app.route('/income/add', methods=['POST'])
def add_income():
    """
    Function that adds a new income record to the database
    """
    # If request method is post then insert the new income record into the database
    db = get_db()
    date = request.form.get('date')
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')

    db.execute('INSERT INTO income (amount, category, description, date, user_id) VALUES (?, ?, ?, ?, ?)',
               [float(request.form['amount']), request.form['category'], request.form['description'], date, session.get('user_id')])

    db.execute('UPDATE users SET balance = balance + ? WHERE id = ?',
               [float(request.form['amount']), session.get('user_id')])
    db.commit()
    # Add message below and redirect back to the income page to display the updated data
    flash('Income added successfully')
    return redirect(url_for('show_income'))

@app.route('/edit', methods=['POST'])
def edit_income():
    """
    Function that edits an income record
    """
    db = get_db()
    old_amount = db.execute('SELECT amount FROM income WHERE id = ? AND user_id = ?',
                            [request.form['id'], session.get('user_id')]).fetchone()['amount']

    db.execute("UPDATE income SET amount = ?, category = ?, description = ?, date = ? WHERE id = ? AND user_id = ?",
               [float(request.form['amount']), request.form['category'], request.form['description'], request.form['date'], request.form['id'], session.get('user_id')])

    db.execute('UPDATE users SET balance = balance + ? WHERE id = ?',
               [float(request.form['amount']) - old_amount, session.get('user_id')])
    db.commit()
    flash('Income was successfully edited')
    return redirect(url_for('show_income'))

@app.route("/delete", methods=['POST'])
def delete_income():
    """
    Function that deletes an income record
    """
    db = get_db()
    amount_to_delete = db.execute('SELECT amount FROM income WHERE id = ? AND user_id = ?',
                                  [request.form['id'], session.get('user_id')]).fetchone()['amount']

    db.execute("DELETE FROM income WHERE id = ? AND user_id = ?",
               [request.form['id'], session.get('user_id')])

    db.execute('UPDATE users SET balance = balance - ? WHERE id = ?',
               [amount_to_delete, session.get('user_id')])
    db.commit()
    flash('Income was successfully deleted')
    return redirect(url_for('show_income'))

@app.route('/expenses', methods=['GET'])
def expenses():
    """Expenses Web Page for Finance Tracker++"""
    if not session.get('loggedin'):
        return redirect(url_for('login_page'))
    db = get_db()

    check_subscriptions()

    user_id = session.get('user_id')
    months_graph = 0
    cat_graph = request.args.get('show_graph')

    # when back button is pressed, removes the generated graph
    if request.args.get('back'):
        cat_graph = None
        months_graph_url = None  # resets the url of graph to None
        months_graph_path = os.path.join('static', f'months_graph{user_id}.svg') # path for the graph for current user
        if os.path.exists(months_graph_path):
            os.remove(months_graph_path)  # removes the generated graph

    # when user presses show specific category graph, generates the graph
    if cat_graph:
        df = pd.read_sql('select date, amount from expenses where category = (?) and user_id = (?)',
                         db, params=[cat_graph, user_id])

        current_year = datetime.now().year

        df = df[df['date'].str[:4].astype(int) == current_year] # gets dates only for this year
        df.loc[:, 'month'] = df.loc[:, 'date'].str[5:7] # creates new column with months using indexing
        df_new = df.loc[:, ['month', 'amount']].copy() # new group with months and amounts
        df_grouped = df_new.groupby(by='month').sum() # groups by months and sums amounts for each month

        sns.lineplot(x='month', y='amount', data=df_grouped, color='black', marker='o') # creates a line graph
        months_graph_path = os.path.join('static', f'months_graph{user_id}.svg') # path for the graph

        # axes customization
        plt.title(f"Monthly Expenses of {cat_graph} for {current_year}", weight="bold")
        plt.xlabel("Months", weight="bold")
        plt.ylabel("Total Expenses ($)", weight="bold")

        plt.savefig(months_graph_path, format='svg')  # saves a generated plot as an .svg file in "static" folder
        plt.close()

    months_graph_path = os.path.join('static', f'months_graph{user_id}.svg') # path for the graph
    check = os.path.exists(months_graph_path)

    category_chosen = request.args.get('categories_choose')

    # Total Expenses by Categories Graph
    df = pd.read_sql("SELECT * FROM expenses where user_id = (?)", db, params=[session.get('user_id')]) # create a dataframe object
    df_grouped = df.groupby(by="category").sum() # grouped categories to show total amount in each

    sns.barplot(x='category', y='amount', data=df_grouped.sort_values(by='amount', ascending=False).head(5), color="black") # create a bar plot
    totalbarplot_path = os.path.join('static', 'totalbarplot.svg') # path to save the generated graph file

    # Customization of axes and title
    plt.title("Top 5 Expense Categories", weight="bold")
    plt.xlabel("Category", weight="bold")
    plt.ylabel("Amount ($)", weight="bold")

    plt.savefig(totalbarplot_path, format='svg') # saves a generated plot as an .svg file in "static/" folder
    plt.close()

    ''' Finding Total Amount of Expenses '''
    all_expenses_amount = db.execute('select amount from expenses where user_id = (?)',
                                     [session.get('user_id')])

    expenses_grouped = all_expenses_amount.fetchall()
    total_expenses_list = [] # created empty list to put each amount into

    # append each value from list of tuples (using indexing)
    for i in range(len(expenses_grouped)):
        total_expenses_list.append(expenses_grouped[i][0])

    total_expenses_amount = sum(total_expenses_list) # getting sum of the updated amounts' list

    ''' Finding All Categories for the Dropdown List'''
    all_categories = db.execute('select distinct category from expenses where user_id = (?) order by id desc',
                                [session.get('user_id')])

    categories_grouped = all_categories.fetchall()

    # adding each category in a list 'categories'
    categories = []
    for i in range(len(categories_grouped)):
        categories.append(categories_grouped[i][0])

    # setting initial values for categories' name and total amount
    selected_category = ''
    category_total = 0

    # Finding total amount for each category
    each_category_amount = db.execute('select category, sum(amount) from expenses where user_id = (?) group by category',
                                      [session.get('user_id')])

    each_amount = each_category_amount.fetchall()

    # if specific expenses category is chosen:
    if category_chosen:
        ''' Display chosen category of expenses'''
        ct = db.execute('select sum(amount) from expenses where category = (?) and user_id = (?)',
                        [category_chosen, session.get('user_id')])

        category_total = ct.fetchall()[0][0] # indexing into an array of tuples to get the name of category
        selected_category = category_chosen

    cur = db.execute('select id, amount, category, description, date from expenses where user_id = (?) order by date desc',
                     [session.get('user_id')]) # getting values from each column

    sub = db.execute('select id, amount, date, months, description from subscriptions where user_id = (?) order by date desc',
                     [session.get('user_id')]) # getting values from each column

    expenses = cur.fetchall()
    subscriptions = sub.fetchall()

    return render_template('expenses.html', expenses=expenses, subscriptions=subscriptions, total=total_expenses_amount,
                           categories=categories, chosen_category=selected_category, chosen_total=category_total,
                           each_amount=each_amount, plot_url=url_for('static', filename='totalbarplot.svg'),
                           months_graph_url=url_for('static', filename=f'months_graph{user_id}.svg'), df=df, check=check)

def check_subscriptions():
    """Runs when the page refreshes to check for subscriptions and adds them to expenses."""
    db = get_db()
    today = datetime.now().strftime('%Y-%m-%d')

    subscriptions = db.execute('select * from subscriptions where date <= ?', (today,)).fetchall() # gets all subscriptions for today

    for sub in subscriptions:
        user_id = sub['user_id']
        amount = sub['amount']
        description = sub['description']
        months = int(sub['months'])
        current_date = datetime.strptime(sub['date'], '%Y-%m-%d')

        db.execute('INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)',
                   (user_id, amount, 'Subscriptions', today, description)) # inserts today's subscription in expense

        db.execute('UPDATE users SET balance = balance - (?) WHERE id = (?)',
                   [amount, user_id]) # updates the balance

        next_date = current_date + relativedelta(months=+1) # finding the next subscription date

        '''Handles edge cases for short months'''
        last_day_of_next_month = calendar.monthrange(next_date.year, next_date.month)[1]

        if next_date.day > last_day_of_next_month:
            next_date = next_date.replace(day=last_day_of_next_month) # moving the day

        next_date_str = next_date.strftime('%Y-%m-%d')

        # checks if the subscription should continue
        if months > 1:
            db.execute('UPDATE subscriptions SET date = ?, months = months - 1 WHERE id = ?',
                       [next_date_str, sub['id']]) # update subscription with the new date and decrease months
        else:
            db.execute('DELETE FROM subscriptions WHERE id = ?', (sub['id'],)) # remove the subscription if no months left

    db.commit()

@app.route('/add-expense', methods=['POST'])
def add_expense():
    """Adds each expense from to the database"""
    db = get_db()
    date = request.form.get('date')
    current_date = datetime.now().strftime('%Y-%m-%d')

    if not date:
        date = current_date

    # Redirects to the main route if date is in the future
    if date > current_date:
        flash('Please, enter a valid past date!')
        return redirect(url_for('expenses'))

    db.execute('update users set balance = balance - (?) where id = (?)',
               [request.form['purchase_amount'], session.get('user_id')]) # updating the balance

    db.execute('insert into expenses (amount, category, date, description, user_id) values (?, ?, ?, ?, ?)', 
               [request.form['purchase_amount'], request.form['category'], date, 

                request.form['description'], session.get('user_id')]) # adds each value to corresponding column
    db.commit()

    flash('New expense was successfully added!')
    return redirect(url_for('expenses')) # goes to the main expenses' route

@app.route('/edit-expense', methods=['POST']) # created edit route
def edit_expense():
    """Allow the user to edit an expense using expense's id"""
    db = get_db()
    prev_expense = request.form['prev_expense']
    updated_amount = request.form['updated_amount']

    date = request.form.get('updated_date')
    current_date = datetime.now().strftime('%Y-%m-%d')

    # Redirects to the main route if date is in the future
    if date > current_date:
        flash('Please, enter a valid past date!')
        return redirect(url_for('expenses'))

    # updating balance when initial expense was higher than updated expense
    if prev_expense > updated_amount:
        difference = float(prev_expense) - float(updated_amount)
        db.execute('update users set balance = balance + (?)  where id = (?)',
                   [difference, session.get('user_id')])

    # updating balance when initial expense was lower than updated expense
    if prev_expense < updated_amount:
        difference = float(updated_amount) - float(prev_expense)
        db.execute('update users set balance = balance - (?) where id = (?)',
                   [difference, session.get('user_id')])

    db.execute('update expenses set date = (?), category = (?), amount = (?), description = (?) where id = (?) and user_id = (?)',
               [request.form['updated_date'], request.form['updated_category'],
                request.form['updated_amount'], request.form['updated_description'],
                request.form['edited_id'], session.get('user_id')]) # updates each feature in the database
    db.commit()

    flash('Expense was successfully edited!')
    return redirect(url_for('expenses')) # goes to the main expenses' route

@app.route('/delete-expense', methods=['POST']) # created delete route
def delete_expense():
    """Deletes an expense chosen by a user using expense's id, updates the database and redirects to the expenses route."""
    db = get_db()

    deleted_expense_amount = db.execute('select amount from expenses where id = ? and user_id = ?',
                                  [request.form['expense_id'], session.get('user_id')]).fetchone()['amount']

    db.execute('update users set balance = balance + (?) where id = (?)',
               [deleted_expense_amount, session.get('user_id')]) # updating the balance

    db.execute('delete from expenses where id = (?) and user_id = (?)',
               [request.form['expense_id'], session.get('user_id')]) # deletes an expense using its id from database
    db.commit()

    flash('Expense was successfully deleted!')
    return redirect(url_for('expenses'))

@app.route('/add-subscription', methods=['POST'])
def add_subscription():
    """Adds the subscription's expense in the future date specified by the user."""
    db = get_db()

    current_date = datetime.now().strftime('%Y-%m-%d')
    date = request.form.get('sub_date')
    months = request.form.get('months')

    if not date:
        date = current_date

    date_f = datetime.strptime(date, "%Y-%m-%d")
    formatted_date = date_f.strftime("%B %d, %Y")

    if not months:
        months = 1
    else:
        months = int(request.form.get('months'))

    # redirects to the main route if date is in the past
    if date < current_date:
        flash('Please, enter a valid future date!')
        return redirect(url_for('expenses'))

    db.execute('insert into subscriptions (amount, date, months, description, user_id) values (?, ?, ?, ?, ?)',
           [request.form['sub_amount'], date, months, request.form['sub_name'], session.get('user_id')])

    db.commit()

    if (date == current_date) and (months == 1):
        flash('New subscription was deducted today!')

    elif date == current_date:
        flash('New subscription was deducted today and set for upcoming months!')

    else:
        flash(f'New subscription will be deducted on {formatted_date}!')

    return redirect(url_for('expenses'))

@app.route('/edit-subscription', methods=['POST']) # created edit route
def edit_subscription():
    """Allows the user to edit subscriptions using subscription's id"""
    current_date = datetime.now().strftime('%Y-%m-%d')
    db = get_db()

    sub_date = request.form.get('updated_sub_date')
    date_f = datetime.strptime(sub_date, "%Y-%m-%d")
    formatted_date = date_f.strftime("%B %d, %Y")

    # Redirects to the main route if date is in the past
    if sub_date < current_date:
        flash('Please, enter a valid future date!')
        return redirect(url_for('expenses'))

    db.execute('update subscriptions set date = (?), description = (?), amount = (?), months = (?) where id = (?) and user_id = (?)',
        [sub_date, request.form['updated_title'],
         request.form['updated_sub_amount'], request.form['updated_months'],
         request.form['edited_sub_id'], session.get('user_id')])  # updates each feature in the database
    db.commit()

    flash(f'Subscription date was updated to {formatted_date}!')
    return redirect(url_for('expenses'))

@app.route('/delete-subscription', methods=['POST']) # created delete route
def delete_subscription():
    """Deletes chosen subscription from the database."""
    db = get_db()

    db.execute('delete from subscriptions where id = (?) and user_id = (?)',
               [request.form['subscription_id'], session.get('user_id')])  # deletes a subscription using its id from database
    db.commit()

    flash('Subscription was successfully deleted!')
    return redirect(url_for('expenses'))

@app.route('/savings', methods=['GET'])
def show_savings():
    # Need to make changes to SQLite statements to account for savings_goal
    db = get_db()
    savings_goal = db.execute('SELECT savings_goal, savings_name from users WHERE id = ?', [session.get('user_id')]).fetchone()
    savings_goal_exist = savings_goal[0] is not None
    savings_name = savings_goal[1]

    if savings_goal_exist:
        savings =  db.execute('SELECT coalesce(sum(amount), 0.0) from savings WHERE user_id = ?', [session.get('user_id')]).fetchone()
        saved_amount = savings[0]
        total_savings = '${:,.2f}'.format(savings[0])
        percent_saved = format((saved_amount / savings_goal[0]) * 100, '.2f')
        s_percent = round(round(saved_amount / savings_goal[0], 4) * 100, 2)
        savings_goal_display = '${:,.2f}'.format(savings_goal[0])

    else:
        total_savings = 0
        percent_saved = 0
        savings_goal_display = 0
        s_percent = 0.00
    return render_template('savings.html', savings_goal_exist=savings_goal_exist, total_savings=total_savings, percent_saved=percent_saved, savings_goal_display=savings_goal_display, savings_name=savings_name, s_percent=s_percent)

@app.route('/savings/add', methods=['POST'])
def add_savings():
    db = get_db()
    current_goal = db.execute('SELECT savings_goal from users WHERE id = ?', [session.get('user_id')]).fetchone()
    current_goal_exist = current_goal[0] is not None

    if current_goal_exist:
        amount_to_add = request.form['amount_to_add']
        db.execute('INSERT INTO savings (amount, user_id) VALUES (?, ?)', [amount_to_add, session.get('user_id')])
        db.commit()
        flash('Amount added to Savings')
    else:
        new_goal = request.form['savings_goal']
        new_name = request.form['savings_name']
        db.execute('UPDATE users SET savings_goal = ? , savings_name = ? WHERE id = ?', [new_goal, new_name, session.get('user_id')])

        db.commit()
        flash('New savings goal successfully made')

    return redirect(url_for('show_savings'))

@app.route('/savings/subtract', methods=['POST'])
def subtract_savings():
    db = get_db()
    subtract_amount = request.form['subtract_amount']
    subtract_amount = round(float(subtract_amount) * -1, 2)
    db.execute('INSERT INTO savings (amount, user_id) VALUES (?, ?)', [subtract_amount, session.get('user_id')])
    db.commit()
    flash('Amount subtracted from savings')
    return redirect(url_for('show_savings'))

@app.route('/budget', methods=['GET'])
def show_budget():
    month = datetime.now().month
    db = get_db()

    compare_expenses_budget = db.execute('SELECT DISTINCT category FROM expenses  WHERE category NOT IN (SELECT DISTINCT category FROM budget) AND user_id = ? AND CAST(STRFTIME("%m", date) AS INTEGER) = ?', [session.get('user_id'), month])
    expenses_not_in_budget = compare_expenses_budget.fetchall()

    budget_query = """SELECT b.category, b.amount AS budget_amount, COALESCE(e.total_expense, 0.0) AS expense_amount FROM budget b LEFT JOIN (SELECT category, SUM(amount) AS total_expense FROM expenses WHERE user_id = ? AND CAST(STRFTIME("%m", date) AS INTEGER) = ? GROUP BY category) e ON b.category = e.category WHERE b.user_id = ? AND b.month = ?"""

    budget = db.execute(budget_query,
                                 [session.get('user_id'), month, session.get('user_id'), month]).fetchall()
    return render_template('budget.html', budget=budget, expenses_not_in_budget=expenses_not_in_budget)
    
@app.route('/budget/add', methods=['POST'])
def add_budget():
    month = datetime.now().month
    budget_category = request.form['category']
    db = get_db()

    existing_category = db.execute('SELECT * FROM budget WHERE category = ? AND user_id = ?', [budget_category, session.get('user_id')]).fetchone()

    if existing_category:
        flash("Category already exists!")
        return redirect(url_for('show_budget'))

    db.execute('INSERT INTO budget (user_id, amount, category, month) VALUES (?, ?, ?, ?)',
               [session.get('user_id'), request.form['amount'], budget_category, month])
    db.commit()
    # Add message below and redirect back to the budget page to display the updated data
    flash('Budget category added successfully')
    return redirect(url_for('show_budget'))

@app.route('/budget/delete', methods=['POST'])
def delete_budget():
    if session.get('loggedin'):
        category = request.form['category']
        user_id = session.get('user_id')
        db = get_db()
        db.execute('DELETE from budget WHERE category = ? AND user_id = ?', [category, user_id])
        db.commit()
        flash("Budget category successfully deleted")
        return redirect(url_for('show_budget'))
    else:
        return redirect(url_for('home_page'))

@app.route('/savings/edit', methods=['POST'])
def edit_savings():
    if session.get('loggedin'):
        db = get_db()
        new_goal = request.form['new_savings_goal']
        new_name = request.form['new_savings_name']
        db.execute('UPDATE users SET savings_goal = ?, savings_name = ? WHERE id=?', [new_goal, new_name, session.get('user_id')])
        db.commit()
        flash('Savings goal successfully edited')
        return redirect(url_for('show_savings'))
    else:
        return redirect(url_for('home_page'))

@app.route('/savings/delete', methods=['POST'])
def delete_savings():
    if session.get('loggedin'):
        db = get_db()
        db.execute('UPDATE users SET savings_goal = null, savings_name = null WHERE id=?', [session.get('user_id')])
        db.execute('UPDATE savings SET amount = 0.0 WHERE user_id = ?', [session.get('user_id')])
        db.commit()
        flash('Savings goal successfully deleted')
        return redirect(url_for('show_savings'))
    else:
        return redirect(url_for('home_page'))

@app.route('/reports', methods=['GET'])
def reports():
    """
    Function that displays reports for any month or year requested by the user
    """
    db = get_db()
    selected_month = request.args.get('month')
    selected_year = request.args.get('year')

    if not selected_month and not selected_year:
        selected_month = datetime.now().strftime('%Y-%m')
    if not selected_year:
        selected_year = datetime.now().strftime('%Y')

    if selected_month:
        cur = db.execute('''SELECT 'Income' AS type, amount, category, description, date FROM income WHERE user_id = ? AND strftime('%Y-%m', date) = ?
                        UNION ALL 
                        SELECT 'Expenses' AS type, amount, category, description, date FROM expenses WHERE user_id = ? AND strftime('%Y-%m', date) = ? ORDER BY date DESC;''',
                         [session.get('user_id'), selected_month, session.get('user_id'), selected_month])
        report_data = cur.fetchall()

        cur = db.execute('SELECT coalesce(sum(amount), 0.0) FROM income WHERE user_id = ? AND strftime("%Y-%m", date) = ?',
            [session.get('user_id'), selected_month])
        income_row = cur.fetchone()
        income_sum = income_row[0]

        cur = db.execute('SELECT Coalesce(SUM(amount), 0.0) FROM expenses WHERE user_id = ? AND strftime("%Y-%m", date) = ?',
            [session.get('user_id'), selected_month])
        expenses_row = cur.fetchone()
        expense_sum = expenses_row[0]

    elif selected_year:
        cur = db.execute('''SELECT 'Income' AS type, amount, category, description, date FROM income WHERE user_id = ? AND strftime('%Y', date) = ?
                        UNION ALL 
                        SELECT 'Expenses' AS type, amount, category, description, date FROM expenses WHERE user_id = ? AND strftime('%Y', date) = ? ORDER BY date DESC;''',
                         [session.get('user_id'), selected_year, session.get('user_id'), selected_year])
        report_data = cur.fetchall()

        cur = db.execute('SELECT coalesce(sum(amount), 0.0) FROM income WHERE user_id = ? AND strftime("%Y", date) = ?',
                         [session.get('user_id'), selected_year])
        income_row = cur.fetchone()
        income_sum = income_row[0]

        cur = db.execute('SELECT Coalesce(SUM(amount), 0.0) FROM expenses WHERE user_id = ? AND strftime("%Y", date) = ?',
            [session.get('user_id'), selected_year])
        expenses_row = cur.fetchone()
        expense_sum = expenses_row[0]

    net_income = income_sum - expense_sum

    return render_template('reports.html', report_data=report_data, income=income_sum, expenses=expense_sum, net_income=net_income, selected_month=selected_month, selected_year=selected_year)

@app.route('/download_pdf', methods=['GET'])
def download_pdf():
    db = get_db()
    selected_month = request.args.get('month')
    selected_year = request.args.get('year')

    if not selected_month and not selected_year:
        selected_month = datetime.now().strftime('%Y-%m')
    if not selected_year:
        selected_year = datetime.now().strftime('%Y')

    if selected_month:
        cur = db.execute("SELECT amount, category, description, date FROM income WHERE user_id = ? AND strftime('%Y-%m', date) = ? ORDER BY date DESC",
            [session.get('user_id'), selected_month])
        income_data = cur.fetchall()

        cur = db.execute("SELECT amount, category, description, date FROM expenses WHERE user_id = ? AND strftime('%Y-%m', date) = ? ORDER BY date DESC",
            [session.get('user_id'), selected_month])
        expenses_data = cur.fetchall()

        cur = db.execute("SELECT COALESCE(SUM(amount), 0) FROM income WHERE user_id = ? AND strftime('%Y-%m', date) = ?",
            [session.get('user_id'), selected_month])
        total_income = cur.fetchone()[0]

        cur = db.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE user_id = ? AND strftime('%Y-%m', date) = ?",
            [session.get('user_id'), selected_month])
        total_expenses = cur.fetchone()[0]

    elif selected_year:
        cur = db.execute("SELECT amount, category, description, date FROM income WHERE user_id = ? AND strftime('%Y', date) = ? ORDER BY date DESC",
            [session.get('user_id'), selected_year])
        income_data = cur.fetchall()

        cur = db.execute("SELECT amount, category, description, date FROM expenses WHERE user_id = ? AND strftime('%Y', date) = ? ORDER BY date DESC",
            [session.get('user_id'), selected_year])
        expenses_data = cur.fetchall()

        cur = db.execute("SELECT COALESCE(SUM(amount), 0) FROM income WHERE user_id = ? AND strftime('%Y', date) = ?",
                         [session.get('user_id'), selected_year])
        total_income = cur.fetchone()[0]

        cur = db.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE user_id = ? AND strftime('%Y', date) = ?",
                         [session.get('user_id'), selected_year])
        total_expenses = cur.fetchone()[0]

    net_income = total_income - total_expenses

    html = render_template('reports_pdf.html', selected_month=selected_month, selected_year=selected_year, income_data=income_data, expenses_data=expenses_data, total_income=total_income, total_expenses=total_expenses, net_income=net_income)

    response = make_response()
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=Financial_Report.pdf'

    pdf = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=pdf)
    if pisa_status.err:
        return "Error generating PDF", 500

    pdf.seek(0)
    response.data = pdf.read()
    return response

@app.route('/settings', methods=['GET'])
def settings():
    db = get_db()
    # Get User info
    cur = db.execute('SELECT username, balance, savings_name FROM users WHERE id = ?',
                     [session.get('user_id')])
    user_info = cur.fetchone()
    return render_template('settings.html', user_info=user_info)

@app.route('/change_password_post', methods=['POST'])
def change_password_post():
    username = request.form['username']
    password = request.form['password']

    # Check if account exists
    db = get_db()
    cur = db.execute('select * from users where username = ? and password = ?',
                     [username, generate_password_hash(password)])
    user = cur.fetchone()

    # If account exists in users table in our database
    if user and session['username'] == username:
        new_password = request.form['new_password']
        new_password2 = request.form['new_password2']

        if new_password2 == new_password:
            db.execute("update users set password = ? where username = ?",
                       [generate_password_hash(new_password), username])
            db.commit()
            return redirect(url_for('home_page'))
    else:
        # Account doesn't exist or username/password incorrect
        flash('Incorrect username/password!')
    return redirect(url_for('change_username'))


@app.route('/change_password', methods=['GET'])
def change_password():
    if request.method == 'GET':
        return render_template('change_password.html')


@app.route('/change_username_post', methods=['POST'])
def change_username_post():
    username = request.form['username']

    password = request.form['password']

    # Check if account exists
    db = get_db()
    cur = db.execute('select * from users where username = ?',
                     [username])
    user = cur.fetchone()

    if  check_password_hash(user['password'],password):
        new_username = request.form['new_username']
        cur2 = db.execute('select * from users where username = ?',[new_username])
        no_user = cur2.fetchone()

        if no_user:
            flash('Username already exists')
            return redirect(url_for('change_username'))

        # If account exists in users table in our database
        if user and session['username'] == username:
            db.execute('update users set username = ? where username = ?',
                             [new_username, username])
            db.commit()

            session['username'] = new_username
            return redirect(url_for('home_page'))
        else:
            # Account doesn't exist or username/password incorrect
            flash('Incorrect username/password!')

    return redirect(url_for('change_username'))


@app.route('/change_username', methods=['GET'])
def change_username():
    if request.method == 'GET':
        return render_template('change_username.html')


@app.context_processor
def inject_user_list():
    db = get_db()

    # Do some admin check here
    # If user is not admin make the Userlist only return the users username
    # placeholder
    cur = db.execute('SELECT admin FROM users WHERE id = ?',
                     [session.get('real_id')])
    is_admin = cur.fetchone()

    if is_admin:
        cur = db.execute('SELECT username from users ORDER BY username collate NOCASE')
        user_list = cur.fetchall()
    else:
        cur = db.execute('SELECT username from users where id = ?',
                         [session.get('real_id')])
        user_list = cur.fetchall()

    return dict(user_list=user_list, is_admin=is_admin)

@app.route('/admin_mask', methods=['GET'])
def admin_mask():
    if session.get('loggedin'):
        db = get_db()
        mask = request.args.get('mask')
        # print(mask)

        # if not valid user is selected then mask is admin's username
        if mask is None or '':
            return redirect(url_for('home_page'))
        cur = db.execute('SELECT id FROM users WHERE username = ?',
                   [mask])
        mask_row = cur.fetchone()
        mask_id = mask_row[0]
        session['user_id'] = mask_id
        return redirect(url_for('home_page'))
    else:
        return redirect(url_for('login_page'))

@app.route('/delete_account', methods=['GET'])
def delete_account():
    # get the current user_id and username
    user_id = session.get('user_id')
    username = session.get('username')

    #set up the database and see if the user is an admin
    db = get_db()
    admin = db.execute('SELECT admin FROM users WHERE username = ?', [username])

    # delete the user based on their user_id
    db.execute('DELETE FROM users WHERE id = ?', [user_id])
    db.commit()

    # if they are an admin, change back to their id and return to the settings page
    if admin.fetchone()[0]:
        session['user_id'] = db.execute('SELECT id FROM users WHERE username = ?', [username]).fetchone()[0]
        return redirect(url_for('settings'))

    # if they are not an admin, logout
    return redirect(url_for('logout'))
