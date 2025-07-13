import os
import app
import unittest
import tempfile

class IncomeTests(unittest.TestCase):
    def setUp(self):
        self.db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
        app.app.testing = True
        self.app = app.app.test_client()
        with app.app.app_context():
            app.init_db()
        with self.app as client:
            with client.session_transaction() as sess:
                sess['id'] = 1

        self.app.post('/register_account', data=dict(
            username = 'testing',
            password = 'testing',
        ), follow_redirects=True)
        self.app.post('/login_account', data=dict(
            username='testing',
            password='testing',
        ), follow_redirects=True)


    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.app.config['DATABASE'])

    # this test will add income through the income url and check to see on the page data if it worked
    def test_add_income(self):
        rv = self.app.post('/income/add', data=dict(
            amount = 1.0,
            category = 'category',
            description = 'description',
            date = '2024-01-01'
        ), follow_redirects=True)

        assert b'Income added successfully' in rv.data
        assert b'1.0' in rv.data
        assert b'category' in rv.data
        assert b'description' in rv.data
        assert b'2024-01-01' in rv.data

    # this test will add income through the income url and check to see on the page data if it worked
    def test_edit_income(self):
        rv = self.app.post('/income/add', data=dict(
            amount=2.0,
            category='cat1',
            description='desc1',
            date='2024-01-01'
        ), follow_redirects=True)

        assert b'Income added successfully' in rv.data
        assert b'2.0' in rv.data
        assert b'cat1' in rv.data
        assert b'desc1' in rv.data
        assert b'2024-01-01' in rv.data

        rv = self.app.post('/edit', data=dict(
            amount=100.0,
            category='cat2',
            description='desc2',
            date='2024-01-02',
            id = 1
        ), follow_redirects=True)

        assert b'Income was successfully edited' in rv.data
        assert b'2.0' not in rv.data
        assert b'cat1' not in rv.data
        assert b'desc1' not in rv.data
        assert b'2024-01-01' not in rv.data

        assert b'100.0' in rv.data
        assert b'cat2' in rv.data
        assert b'desc2' in rv.data
        assert b'2024-01-02' in rv.data

    def test_delete_income(self):
        rv = self.app.post('/income/add', data=dict(
            amount=2.0,
            category='cat1',
            description='desc1',
            date='2024-01-01'
        ), follow_redirects=True)

        assert b'Income added successfully' in rv.data
        assert b'2.0' in rv.data
        assert b'cat1' in rv.data
        assert b'desc1' in rv.data
        assert b'2024-01-01' in rv.data

        rv = self.app.post('/delete', data=dict(
            id = 1
        ), follow_redirects=True)

        assert b'Income was successfully deleted' in rv.data
        assert b'2.0' not in rv.data
        assert b'cat1' not in rv.data
        assert b'desc1' not in rv.data
        assert b'2024-01-01' not in rv.data

    def test_delete_add_income(self):
        rv = self.app.post('/income/add', data=dict(
            amount=2.0,
            category='cat1',
            description='desc1',
            date='2024-01-01'
        ), follow_redirects=True)

        assert b'Income added successfully' in rv.data
        assert b'2.0' in rv.data
        assert b'cat1' in rv.data
        assert b'desc1' in rv.data
        assert b'2024-01-01' in rv.data

        rv = self.app.post('/income/add', data=dict(
            amount=1.0,
            category='cat2',
            description='desc2',
            date='2024-01-02'
        ), follow_redirects=True)

        assert b'Income added successfully' in rv.data
        assert b'1.0' in rv.data
        assert b'cat2' in rv.data
        assert b'desc2' in rv.data
        assert b'2024-01-02' in rv.data

        rv = self.app.post('/delete', data=dict(
            id = 1
        ), follow_redirects=True)

        assert b'Income was successfully deleted' in rv.data
        assert b'2.0' not in rv.data
        assert b'cat1' not in rv.data
        assert b'desc1' not in rv.data
        assert b'2024-01-01' not in rv.data

        assert b'1.0' in rv.data
        assert b'cat2' in rv.data
        assert b'desc2' in rv.data
        assert b'2024-01-02' in rv.data

    def test_edit_add_income(self):
        rv = self.app.post('/income/add', data=dict(
            amount=2.0,
            category='cat1',
            description='desc1',
            date='2024-01-01'
        ), follow_redirects=True)

        assert b'Income added successfully' in rv.data
        assert b'2.0' in rv.data
        assert b'cat1' in rv.data
        assert b'desc1' in rv.data
        assert b'2024-01-01' in rv.data

        rv = self.app.post('/income/add', data=dict(
            amount=1.0,
            category='cat2',
            description='desc2',
            date='2024-01-02'
        ), follow_redirects=True)

        assert b'Income added successfully' in rv.data
        assert b'1.0' in rv.data
        assert b'cat2' in rv.data
        assert b'desc2' in rv.data
        assert b'2024-01-02' in rv.data

        rv = self.app.post('/edit', data=dict(
            amount=100.0,
            category='cat3',
            description='desc3',
            date='2024-01-03',
            id=1
        ), follow_redirects=True)

        assert b'Income was successfully edited' in rv.data
        assert b'2.0' not in rv.data
        assert b'cat1' not in rv.data
        assert b'desc1' not in rv.data
        assert b'2024-01-01' not in rv.data

        assert b'1.0' in rv.data
        assert b'cat2' in rv.data
        assert b'desc2' in rv.data
        assert b'2024-01-02' in rv.data

        assert b'100.0' in rv.data
        assert b'cat3' in rv.data
        assert b'desc3' in rv.data
        assert b'2024-01-03' in rv.data

    def test_edit2_add_income(self):
        rv = self.app.post('/income/add', data=dict(
            amount=2.0,
            category='cat1',
            description='desc1',
            date='2024-01-01'
        ), follow_redirects=True)

        assert b'Income added successfully' in rv.data
        assert b'2.0' in rv.data
        assert b'cat1' in rv.data
        assert b'desc1' in rv.data
        assert b'2024-01-01' in rv.data

        rv = self.app.post('/income/add', data=dict(
            amount=1.0,
            category='cat2',
            description='desc2',
            date='2024-01-02'
        ), follow_redirects=True)

        assert b'Income added successfully' in rv.data
        assert b'1.0' in rv.data
        assert b'cat2' in rv.data
        assert b'desc2' in rv.data
        assert b'2024-01-02' in rv.data

        rv = self.app.post('/edit', data=dict(
            amount=3.0,
            category='cat3',
            description='desc3',
            date='2024-01-03',
            id=2
        ), follow_redirects=True)

        assert b'Income was successfully edited' in rv.data
        assert b'2.0' in rv.data
        assert b'cat1' in rv.data
        assert b'desc1' in rv.data
        assert b'2024-01-01' in rv.data

        assert b'cat2' not in rv.data
        assert b'desc2' not in rv.data
        assert b'2024-01-02' not in rv.data

        assert b'3.0' in rv.data
        assert b'cat3' in rv.data
        assert b'desc3' in rv.data
        assert b'2024-01-03' in rv.data

class ExpensesTests(unittest.TestCase):
    def setUp(self):
        self.db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
        app.app.testing = True
        self.app = app.app.test_client()
        with app.app.app_context():
            app.init_db()
        with self.app as client:
            with client.session_transaction() as sess:
                sess['id'] = 1

        self.app.post('/register_account', data=dict(
            username = 'testing',
            password = 'testing',
        ), follow_redirects=True)
        self.app.post('/login_account', data=dict(
            username='testing',
            password='testing',
        ), follow_redirects=True)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.app.config['DATABASE'])

    def test_add_expense(self):
        rv = self.app.post('/add-expense', data=dict(
            category = 'cat1',
            purchase_amount = 1.0,
            description = 'desc1',
            date = '2024-01-01',
        ), follow_redirects=True)
        assert b'New expense was successfully added!' in rv.data
        assert b'1.0' in rv.data
        assert b'cat1' in rv.data
        assert b'desc1' in rv.data
        assert b'2024-01-01' in rv.data

    def test_edit_expense(self):
        rv = self.app.post('/add-expense', data=dict(
            category = 'cat1',
            purchase_amount = 2.0,
            description = 'desc1',
            date = '2024-01-01',
        ), follow_redirects=True)

        assert b'New expense was successfully added!' in rv.data
        assert b'2.0' in rv.data
        assert b'cat1' in rv.data
        assert b'desc1' in rv.data
        assert b'2024-01-01' in rv.data

        rv = self.app.post('/edit-expense', data=dict(
            updated_category='cat2',
            updated_amount=3.0,
            updated_description='desc2',
            updated_date='2024-01-02',
            edited_id=1,
            prev_expense=2.0
        ), follow_redirects=True)

        # rv = self.app.get('/expenses')
        assert b'Expense was successfully edited!' in rv.data
        assert b'2.0' not in rv.data
        assert b'cat1' not in rv.data
        assert b'desc1' not in rv.data
        assert b'2024-01-01' not in rv.data

        assert b'3.0' in rv.data
        assert b'cat2' in rv.data
        assert b'desc2' in rv.data
        assert b'2024-01-02' in rv.data

    def test_delete_expense(self):
        rv = self.app.post('/add-expense', data=dict(
            category = 'cat1',
            purchase_amount = 2.0,
            description = 'desc1',
            date = '2024-01-01',
        ), follow_redirects=True)

        assert b'New expense was successfully added!' in rv.data
        assert b'2.0' in rv.data
        assert b'cat1' in rv.data
        assert b'desc1' in rv.data
        assert b'2024-01-01' in rv.data

        rv = self.app.post('/delete-expense', data=dict(
            expense_id=1,
        ), follow_redirects=True)

        # rv = self.app.get('/expenses')
        assert b'Expense was successfully deleted!' in rv.data
        assert b'2.0' not in rv.data
        assert b'cat1' not in rv.data
        assert b'desc1' not in rv.data
        assert b'2024-01-01' not in rv.data

    def test_delete_add_expense(self):
        rv = self.app.post('/add-expense', data=dict(
            category = 'cat1',
            purchase_amount = 2.0,
            description = 'desc1',
            date = '2024-01-01',
        ), follow_redirects=True)

        assert b'New expense was successfully added!' in rv.data
        assert b'2.0' in rv.data
        assert b'cat1' in rv.data
        assert b'desc1' in rv.data
        assert b'2024-01-01' in rv.data

        rv = self.app.post('/add-expense', data=dict(
            category='cat2',
            purchase_amount=3.0,
            description='desc2',
            date='2024-01-02',
        ), follow_redirects=True)

        assert b'New expense was successfully added!' in rv.data
        assert b'3.0' in rv.data
        assert b'cat2' in rv.data
        assert b'desc2' in rv.data
        assert b'2024-01-02' in rv.data

        rv = self.app.post('/delete-expense', data=dict(
            expense_id=1,
        ), follow_redirects=True)

        # rv = self.app.get('/expenses')
        assert b'Expense was successfully deleted!' in rv.data
        assert b'2.0' not in rv.data
        assert b'cat1' not in rv.data
        assert b'desc1' not in rv.data
        assert b'2024-01-01' not in rv.data

        assert b'3.0' in rv.data
        assert b'cat2' in rv.data
        assert b'desc2' in rv.data
        assert b'2024-01-02' in rv.data

    def test_edit_add_expense(self):
        rv = self.app.post('/add-expense', data=dict(
            category = 'cat1',
            purchase_amount = 2.0,
            description = 'desc1',
            date = '2024-01-01',
        ), follow_redirects=True)

        assert b'New expense was successfully added!' in rv.data
        assert b'2.0' in rv.data
        assert b'cat1' in rv.data
        assert b'desc1' in rv.data
        assert b'2024-01-01' in rv.data

        rv = self.app.post('/add-expense', data=dict(
            category='cat2',
            purchase_amount=3.0,
            description='desc2',
            date='2024-01-02',
        ), follow_redirects=True)

        assert b'New expense was successfully added!' in rv.data
        assert b'3.0' in rv.data
        assert b'cat2' in rv.data
        assert b'desc2' in rv.data
        assert b'2024-01-02' in rv.data

        rv = self.app.post('/edit-expense', data=dict(
            updated_category='cat3',
            updated_amount=4.0,
            updated_description='desc3',
            updated_date='2024-01-03',
            edited_id=1,
            prev_expense=2.0
        ), follow_redirects=True)

        # rv = self.app.get('/expenses')
        assert b'Expense was successfully edited!' in rv.data
        assert b'2.0' not in rv.data
        assert b'cat1' not in rv.data
        assert b'desc1' not in rv.data
        assert b'2024-01-01' not in rv.data

        assert b'4.0' in rv.data
        assert b'cat3' in rv.data
        assert b'desc3' in rv.data
        assert b'2024-01-03' in rv.data

        assert b'3.0' in rv.data
        assert b'cat2' in rv.data
        assert b'desc2' in rv.data
        assert b'2024-01-02' in rv.data

class BudgetLimit(unittest.TestCase):
    def setUp(self):
        self.db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
        app.app.testing = True
        self.app = app.app.test_client()
        with app.app.app_context():
            app.init_db()
        with self.app as client:
            with client.session_transaction() as sess:
                sess['id'] = 1

        self.app.post('/register_account', data=dict(
            username = 'testing',
            password = 'testing',
        ), follow_redirects=True)
        self.app.post('/login_account', data=dict(
            username='testing',
            password='testing',
        ), follow_redirects=True)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.app.config['DATABASE'])

    def test_budget_limit(self):
        rv = self.app.post('/budget/add', data=dict(
            category = 'cat1',
            amount = 7.00,
            month = 12,
        ), follow_redirects=True)
        assert b'Budget category added successfully' in rv.data
        assert b'cat1' in rv.data
        assert b'7.00' in rv.data

    def test_budget_limit2(self):
        rv = self.app.post('/budget/add', data=dict(
            category = 'cat1',
            amount = 7.00,
            month = 12,
        ), follow_redirects=True)
        assert b'Budget category added successfully' in rv.data
        assert b'cat1' in rv.data
        assert b'7.00' in rv.data

        rv = self.app.post('/budget/add', data=dict(
            category='cat2',
            amount=14.00,
            month = 12,
        ), follow_redirects=True)
        assert b'Budget category added successfully' in rv.data
        assert b'cat2' in rv.data
        assert b'14.00' in rv.data

        assert b'cat1' in rv.data
        assert b'7.00' in rv.data

    def test_budget_delete(self):
        rv = self.app.post('/budget/add', data=dict(
            category = 'cat1',
            amount = 7.00,
            month = 12,
        ), follow_redirects=True)
        assert b'Budget category added successfully' in rv.data
        assert b'cat1' in rv.data
        assert b'7.00' in rv.data

        rv = self.app.post('/budget/add', data=dict(
            category='cat2',
            amount=14.00,
            month = 12,
        ), follow_redirects=True)
        assert b'Budget category added successfully' in rv.data
        assert b'cat2' in rv.data
        assert b'14.00' in rv.data

        assert b'cat1' in rv.data
        assert b'7.00' in rv.data

        rv = self.app.post('/budget/delete', data=dict(
            category='cat2',
        ), follow_redirects=True)

        assert b'Budget category successfully deleted' in rv.data
        assert b'cat2' not in rv.data
        assert b'14.00' not in rv.data

        assert b'cat1' in rv.data
        assert b'7.00' in rv.data

class SavingsGoalTests(unittest.TestCase):
    def setUp(self):
        self.db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
        app.app.testing = True
        self.app = app.app.test_client()
        with app.app.app_context():
            app.init_db()
        with self.app as client:
            with client.session_transaction() as sess:
                sess['id'] = 1

        self.app.post('/register_account', data=dict(
            username = 'testing',
            password = 'testing',
        ), follow_redirects=True)
        self.app.post('/login_account', data=dict(
            username='testing',
            password='testing',
        ), follow_redirects=True)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.app.config['DATABASE'])

    def test_create_savings_goal(self):
        rv = self.app.post('/savings/add', data=dict(
            savings_goal = 10,
            savings_name = 'testing',
        ), follow_redirects=True)
        assert b'You are <strong>0.00%</strong> of the way to your goal!' in rv.data
        assert b'10.00' in rv.data

    def test_savings_goal(self):
        rv = self.app.post('/savings/add', data=dict(
            savings_goal = 10,
            savings_name = 'testing',
        ), follow_redirects=True)
        assert b'You are <strong>0.00%</strong> of the way to your goal!' in rv.data
        assert b'10.00' in rv.data
        # assert b'testing' in rv.data

        rv = self.app.post('/savings/add', data=dict(
            amount_to_add=5,
        ), follow_redirects=True)
        assert b'You are <strong>50.00%</strong> of the way to your goal!' in rv.data
        assert b'5.00' in rv.data
        assert b'10.00' in rv.data
        # assert b'testing' in rv.data

class HomepageTests(unittest.TestCase):
    def setUp(self):
        self.db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
        app.app.testing = True
        self.app = app.app.test_client()
        with app.app.app_context():
            app.init_db()
        with self.app as client:
            with client.session_transaction() as sess:
                sess['id'] = 1

        self.app.post('/register_account', data=dict(
            username = 'testing',
            password = 'testing',
        ), follow_redirects=True)
        self.app.post('/login_account', data=dict(
            username='testing',
            password='testing',
        ), follow_redirects=True)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.app.config['DATABASE'])

    def test_homepage_income(self):
        rv = self.app.post('/income/add', data=dict(
            amount=2.0,
            category='category',
            description='description',
            date='2024-01-01'
        ), follow_redirects=True)

        assert b'Income added successfully' in rv.data
        assert b'2.0' in rv.data
        assert b'category' in rv.data
        assert b'description' in rv.data
        assert b'2024-01-01' in rv.data

        rv = self.app.get('/', data=dict())
        assert b'2.0' in rv.data

    def test_homepage_income_expense(self):
        rv = self.app.post('/income/add', data=dict(
            amount=100.0,
            category='category',
            description='description',
            date='2024-01-01'
        ), follow_redirects=True)

        assert b'Income added successfully' in rv.data
        assert b'100.0' in rv.data
        assert b'category' in rv.data
        assert b'description' in rv.data
        assert b'2024-01-01' in rv.data

        rv = self.app.get('/', data=dict())
        assert b'100.0' in rv.data

        rv = self.app.post('/add-expense', data=dict(
            category='cat1',
            purchase_amount=5.0,
            description='desc1',
            date='2024-01-01',
        ), follow_redirects=True)
        assert b'New expense was successfully added!' in rv.data
        assert b'5.0' in rv.data
        assert b'cat1' in rv.data
        assert b'desc1' in rv.data
        assert b'2024-01-01' in rv.data

        rv = self.app.get('/', data=dict())
        assert b'95.0' in rv.data
        assert b'100.0' in rv.data
        assert b'5.0' in rv.data


    def test_homepage_savings(self):
        rv = self.app.post('/savings/add', data=dict(
            savings_goal=10,
            savings_name='testing',
        ), follow_redirects=True)
        assert b'10.00' in rv.data

        rv = self.app.get('/', data=dict())
        assert b'10.0' in rv.data
class ReportTests(unittest.TestCase):
    def setUp(self):
        self.db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
        app.app.testing = True
        self.app = app.app.test_client()
        with app.app.app_context():
            app.init_db()
        with self.app as client:
            with client.session_transaction() as sess:
                sess['id'] = 1

        self.app.post('/register_account', data=dict(
            username = 'testing',
            password = 'testing',
        ), follow_redirects=True)
        self.app.post('/login_account', data=dict(
            username='testing',
            password='testing',
        ), follow_redirects=True)
        rv = self.app.post('/income/add', data=dict(
            amount=2.0,
            category='cat1',
            description='desc1',
            date='2024-01-01'
        ), follow_redirects=True)

        assert b'Income added successfully' in rv.data
        assert b'2.0' in rv.data
        assert b'cat1' in rv.data
        assert b'desc1' in rv.data
        assert b'2024-01-01' in rv.data

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.app.config['DATABASE'])
    def test_report_income(self):
        rv = self.app.get('/reports?month=2024-01', data=dict())
        assert b'2.0' in rv.data
        assert b'cat1' in rv.data
        assert b'desc1' in rv.data
        assert b'2024-01-01' in rv.data

        rv = self.app.get('/reports?month=2024-02', data=dict())
        assert b'2.0' not in rv.data
        assert b'cat1' not in rv.data
        assert b'desc1' not in rv.data
        assert b'2024-01-01' not in rv.data
        # assert b'1.0' in rv.data

    def test_report_income_expense(self):
        rv = self.app.post('/add-expense', data=dict(
            category='cat2',
            purchase_amount=3.0,
            description='desc2',
            date='2024-01-01',
        ), follow_redirects=True)
        assert b'New expense was successfully added!' in rv.data
        assert b'3.0' in rv.data
        assert b'cat2' in rv.data
        assert b'desc2' in rv.data
        assert b'2024-01-01' in rv.data

        rv = self.app.get('/reports?month=2024-01', data=dict())
        assert b'2.0' in rv.data
        assert b'cat1' in rv.data
        assert b'desc1' in rv.data
        assert b'2024-01-01' in rv.data
        assert b'3.0' in rv.data
        assert b'cat2' in rv.data
        assert b'desc2' in rv.data
        assert b'2024-01-01' in rv.data
        assert b'-1.0' in rv.data

        rv = self.app.get('/reports?month=2024-02', data=dict())
        assert b'2.0' not in rv.data
        assert b'cat1' not in rv.data
        assert b'desc1' not in rv.data
        assert b'2024-01-01' not in rv.data
        assert b'3.0' not in rv.data
        assert b'cat2' not in rv.data
        assert b'desc2' not in rv.data
        assert b'2024-01-01' not in rv.data
        assert b'-1.0' not in rv.data

if __name__ == '__main__':
    unittest.main()
