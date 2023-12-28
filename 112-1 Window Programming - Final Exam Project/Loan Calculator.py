from tkinter import *  # Import tkinter

def cal():
    class _info_prototype:
        def __init__(self):
            class _rate_prototype:
                year = float(rateVar.get())
                month = year / (12 * 100)
            class _time_prototype:
                year = int(yearVar.get())
                month = 12 * year
            class _count_prototype:
                monthly = None
            self.rate = _rate_prototype
            self.time = _time_prototype
            self.count = _count_prototype
            self.balance = float(loanVar.get())
            self.reschedule = rescheduleVar.get()

        @property
        def plan(self): return int(planVar.get()) if planVar.get() else 0
        
        @property
        def quota(self): return int(quotaVar.get()) if planVar.get() else 0

        def counter(self, start=0) -> float:
            month = self.time.month - start
            monthly = (float(self.balance) * (1 + self.rate.month) ** month * self.rate.month) / ((1 + self.rate.month) ** month - 1)
            return monthly

    info = _info_prototype()
    info.count.monthly = info.counter()

    text.config(state=NORMAL)
    pre_monthly = info.count.monthly
    opt = False
    for i in range(info.time.month):
        intst = info.rate.month * info.balance
        opt = True if (i+1 == info.plan and info.reschedule) else False
        if opt:
            info.balance -= info.quota
            info.count.monthly = info.counter(i+1)
        else:
            rpymt = info.count.monthly - intst
            info.balance -= rpymt
        text.insert(INSERT, "    ")
        text.insert(INSERT, str(i+1))
        text.insert(INSERT, "\t\t\t")
        text.insert(INSERT, str(format(rpymt if not opt else info.quota, '.0f')))
        text.insert(INSERT, "\t\t\t")
        text.insert(INSERT, str(format(intst, '.0f')))
        text.insert(INSERT, "\t\t")
        text.insert(INSERT, str(format(info.balance, '.0f')))
        text.insert(END, "\n")
    text.insert(END, f"\n提前還款前月付款：{pre_monthly:.0f}") if opt else ...
    text.config(state=DISABLED)
    monthpayVar.set(int(info.count.monthly))

def clear():
    text.config(state=NORMAL)
    text.delete('1.0', END)
    text.config(state=DISABLED)

def trigger():
    state = NORMAL if rescheduleVar.get() else DISABLED
    Entry_plan.config(state=state)
    Entry_quota.config(state=state)


window = Tk()
window.title("loan calculator")
cframe = Frame(window)
cframe.grid(row=4, column=1, sticky=EW)
yscrollbar = Scrollbar(window)  # y軸scrollbar物件
yscrollbar.grid(row=10, column=6, sticky=NS)
text = Text(window, height=30, width=80, state=DISABLED)  # y軸scrollbar包裝顯示
text.grid(row=10, column=1, columnspan=5, sticky=NS)
yscrollbar.config(command=text.yview)  # y軸scrollbar設定
text.config(yscrollcommand=yscrollbar.set)  # Text控件設定

Label(window, text="貸款年利率").grid(row=1, column=1, sticky=W)
Label(window, text="貸款年數").grid(row=2, column=1, sticky=W)
Label(window, text="貸款金額").grid(row=3, column=1, sticky=W)
Label(cframe, text="提前還款").pack(side=LEFT)
Label(window, text="提前還款時間（月數）").grid(row=5, column=1, sticky=W)
Label(window, text="提前還款金額").grid(row=6, column=1, sticky=W)
Label(window, text="提前還款後月付款").grid(row=7, column=1, sticky=W)

rateVar = StringVar()
Entry(window, textvariable=rateVar, justify=RIGHT).grid(row=1, column=2, padx=3)
yearVar = StringVar()
Entry(window, textvariable=yearVar, justify=RIGHT).grid(row=2, column=2, padx=3)
loanVar = StringVar()
Entry(window, textvariable=loanVar, justify=RIGHT).grid(row=3, column=2, padx=3)
planVar = StringVar()
quotaVar = StringVar()
Entry_plan = Entry(window, textvariable=planVar, justify=RIGHT, state=DISABLED)
Entry_plan.grid(row=5, column=2, padx=3)
Entry_quota = Entry(window, textvariable=quotaVar, justify=RIGHT, state=DISABLED)
Entry_quota.grid(row=6, column=2, padx=3)

rescheduleVar = BooleanVar()
Checkbutton(cframe, variable=rescheduleVar, command=trigger).pack(side=RIGHT)


monthpayVar = StringVar()
Label(window, textvariable=monthpayVar).grid(row=7, column=2, sticky=E, padx=3)
Button(window, text="計算貸款金額", command=cal).grid(row=8, column=2, sticky=E, padx=3, pady=3)
Button(window, text="清除", command=clear).grid(row=8, column=3, sticky=E, padx=3, pady=3)
Label(window, text="期別").grid(row=9, column=1)
Label(window, text="償還本金").grid(row=9, column=2)
Label(window, text="償還利息").grid(row=9, column=3)
Label(window, text="           剩餘本金").grid(row=9, column=4)

# grid和pack回傳的內容是None，所以我把那些存儲None的變數都砍掉了

window.mainloop()