from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField
from wtforms import validators, ValidationError
from wtforms.validators import DataRequired, NumberRange

class LoanForm(FlaskForm):
    loan_type = RadioField('贷款类别', choices = [(1,'公积金贷款'),(2,'混合贷款'),(3,'商业贷款')], validators=[DataRequired("")], coerce=int)
    repay_type = SelectField('还款方式', choices = [(1, '等额本息'), (2, '等额本金')], coerce=int)
    term = SelectField('贷款期限', choices = [(5, '5年'), (10, '10年'), (15, '15年'), (25, '25年'), (30, '30年')], coerce=int)
    f_amount = IntegerField("公积金贷款金额", validators=[NumberRange(0, 99999999)])
    bankId = SelectField('选择银行', choices = [(1, '中国银行'), (2, '工商银行'), (3, '建设银行')], coerce=int)
    b_amount = IntegerField("银行贷款金额", validators=[NumberRange(0, 99999999)])
    submit = SubmitField("计算房贷")