import math

def loan_calculator(amount, rate, term, repay_type):    # 传入的rate要乘100（比如5%传入5）
    if repay_type == 1:                                # 等额本息
        up = amount * math.pow((1 + rate / 1200), term * 12)
        down = 1
        for i in range(1, term * 12):
            down = down + math.pow((1 + rate / 1200), i)
        A = up / down
        total_pay = round(A * term * 12, 2)
        monthly_pay = round(A, 2)
        monthly_decrement = 0
        loan_cal_dict = {}
        loan_cal_dict["total_pay"] = total_pay
        loan_cal_dict["monthly_pay"] = monthly_pay
        loan_cal_dict["monthly_decrement"] = monthly_decrement
        return loan_cal_dict
    elif repay_type == 2:                              # 等额本金
        A = float(amount) / (term * 12)
        B = amount * (rate / 1200)
        C = A * (rate / 1200)
        D = (B + C) * term * 6
        total_pay = round(D + amount, 2)
        monthly_pay = round(A + B, 2)                  # 首月还款
        monthly_decrement = round(C, 2)                # 每月递减
        loan_cal_dict = {}
        loan_cal_dict["total_pay"] = total_pay
        loan_cal_dict["monthly_pay"] = monthly_pay
        loan_cal_dict["monthly_decrement"] = monthly_decrement
        return loan_cal_dict