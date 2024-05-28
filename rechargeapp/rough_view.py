@login_required(login_url=settings.LOGIN_URL)
def CableStartimesView(request):
    template_name = "cables/startime_cable_purchase_template.html"
    return render(request, template_name, {})

@login_required(login_url=settings.LOGIN_URL)
def CableStartimesRechargeView(request):
    user = request.user
    if request.method == "POST":
        phone = request.POST.get('phone')
        smart_no = request.POST.get('smart_no')
        cable_amount = request.POST.get('amt')
        use_credit = request.POST.get('usecredit') 
        ordernumber = 'Star' + get_random_string(length=17)
        smsbal = SmsangoSBulkCredit.objects.get(user=user)
        bonuscre = BonusAccount.objects.get(user=user)
        #Check if to used dasboard credit and if the smscredit is enough to buy the recharge card
        compare = float(int(cable_amount)) <= smsbal.smscredit
        if use_credit == "YES" and compare is True:
            cableapi = ''
            r = requests.post(cableapi)
            info = (r.content).decode("utf-8")
            resp = json.loads(info)
            #checking the API repsonse
            if '100' in info:
                smsbal.smscredit -= Decimal(int(cable_amount))
                smsbal.save()
                obj = CableRecharge.objects.create(
                    user = user,
                    ordernumber = ordernumber,
                    smart_no = smart_no,
                    sub_amount = int(cable_amount),
                    phone = phone,
                    billtype = "Startimes",
                    messageresp = resp['message'],
                    exchange_reference = resp['exchangeReference']
                )
                bonuscre.bonus += Decimal(.001 * int(cable_amount))
                bonuscre.save()
                return render(request, 'airtime/successful_recharge_card.html')
            else:
                obj = CableRecharge.objects.create(
                    user = user,
                    ordernumber = ordernumber,
                    smart_no = smart_no,
                    sub_amount = int(cable_amount),
                    phone = phone,
                    billtype = "Startimes",
                    messageresp = "Failed",
                    #exchange_reference = resp['exchangeReference']
                )
                return render(request, 'paystack/failure.html')
        elif use_credit == "NO":
            context = {
                'smart_no' : smart_no,
                'phone'  : phone,
                'amt' : int(cable_amount) * 100,
                'ordernumber' : ordernumber,
            }
            return render(request, 'cable/cable_atm_recharge_page_data.html', context)
        else:
            return render(request, 'paystack/failure.html', {})
    else:
        return render(request, 'paystack/failure.html', {})

def AtmStartimesPaystack(request):
    user = request.user
    ordernumber = request.POST.get('paystack-trxref')
    # reference = request.POST.get('reference')
    cable_amount = request.POST.get('amount')
    phone = request.POST.get('phone')
    smart_no = request.POST.get('smart_no')
	# print(custom)
	# print(amount)
    #Using ATM/BANK ==> PAYSTACK PROCEDURE SO AFTER PAYMENT ACCESS THE API TO RECHARGE USER 
    if ordernumber:
        cableapi = ''
        r = requests.post(cableapi)
        info = (r.content).decode("utf-8")
        resp = json.loads(info)
        #checking the API repsonse
        if '100' in info:
            obj = CableRecharge.objects.create(
                user = user,
                ordernumber = ordernumber,
                smart_no = smart_no,
                sub_amount = int(cable_amount)/100,
                phone = phone,
                billtype = "Startimes",
                messageresp = resp['message'],
                exchange_reference = resp['exchangeReference']
            )
            return render(request, 'airtime/successful_recharge_card.html')
        else:
            obj = CableRecharge.objects.create(
                user = user,
                ordernumber = ordernumber,
                smart_no = smart_no,
                sub_amount = int(cable_amount)/100,
                phone = phone,
                billtype = "Startimes",
                messageresp = "Failed",
                #exchange_reference = resp['exchangeReference']
            )        
            return render(request, 'paystack/failure.html')
    else:
        return render(request, 'paystack/failure.html')


@login_required(login_url=settings.LOGIN_URL)
def CableGotvDstvView(request):
    template_name = "cables/cable_purchase_template.html"
    return render(request, template_name, {})

@login_required(login_url=settings.LOGIN_URL)
def CableGotvDstvRechargeView(request):
    user = request.user
    if request.method == "POST":
        invoice = request.POST.get('invoice')
        customer_name = request.POST.get('customer_name')
        customer_number = request.POST.get('customer_number')
        smart_no = request.POST.get('smart_no')
        phone = request.POST.get('phone')
        billtype = request.POST.get('billtype')
        cable_amount = request.POST.get('amt')
        use_credit = request.POST.get('usecredit') 
        ordernumber = 'GD' + get_random_string(length=17)
        smsbal = SmsangoSBulkCredit.objects.get(user=user)
        bonuscre = BonusAccount.objects.get(user=user)
        #Check if to used dasboard credit and if the smscredit is enough to buy the recharge card
        compare = float(int(cable_amount)) <= smsbal.smscredit
        if use_credit == "YES" and compare is True:
            cableapi ='' 
            r = requests.post(cableapi)
            info = (r.content).decode("utf-8")
            resp = json.loads(info)
            #checking the API repsonse
            if '100' in info:
                smsbal.smscredit -= Decimal(int(cable_amount))
                smsbal.save()
                obj = CableRecharge.objects.create(
                    user = user,
                    ordernumber = ordernumber,
                    smart_no = smart_no,
                    phone = phone,
                    sub_amount = int(cable_amount)/100,
                    customernumber = customer_number,
                    customername = customer_name,
                    billtype = billtype,
                    messageresp = resp['message'],
                    invoice = invoice,
                    exchange_reference = resp['exchangeReference']
                )
                bonuscre.bonus += Decimal(.001 * int(cable_amount))
                bonuscre.save()
                return render(request, 'airtime/successful_recharge_card.html')
            else:
                obj = CableRecharge.objects.create(
                    user = user,
                    ordernumber = ordernumber,
                    smart_no = smart_no,
                    phone = phone,
                    sub_amount = int(cable_amount)/100,
                    customernumber = customer_number,
                    customername = customer_name,
                    billtype = billtype,
                    messageresp = "Failed",
                    invoice = invoice,
                    #exchange_reference = resp['exchangeReference']
                )
                return render(request, 'paystack/failure.html')
        elif use_credit == "NO":
            context = {
                'smart_no' : smart_no,
                'phone' : phone,
                'billtype'  : billtype,
                'amt' : int(cable_amount) * 100,
                'ordernumber' : ordernumber,
                'invoice' : invoice,
                'customername' : customer_name,
                'customer_number' : customer_number

            }
            return render(request, 'cable/cable_GS_atm_recharge_page_data.html', context)
        else:
            return render(request, 'paystack/failure.html', {})
    else:
        return render(request, 'paystack/failure.html', {})

def AtmGotvDstvPaystack(request):
    user = request.user
    ordernumber = request.POST.get('paystack-trxref')
    invoice = request.POST.get('invoice')
    customer_name = request.POST.get('customer_name')
    customer_number = request.POST.get('customer_number')
    cable_amount = request.POST.get('amount')
    smart_no = request.POST.get('smart_no')
    phone = request.POST.get('phone')
    billtype = request.POST.get('billtype')
    bonuscre = BonusAccount.objects.get(user=user)
    #Using ATM/BANK ==> PAYSTACK PROCEDURE SO AFTER PAYMENT ACCESS THE API TO RECHARGE USER 
    if ordernumber:
        cableapi = 'https://mobileairtimeng.com/httpapi/multichoice?userid=08181384092&pass=35bd15488e89a2c32c90&phone='+phone+'&amt='+cable_amount+'&smartno='+smart_no+'&customer='+customer_name+'&invoice='+invoice+'&billtype='+billtype+'&customernumber='+customer_number+'&jsn=json'
        r = requests.post(cableapi)
        info = (r.content).decode("utf-8")
        resp = json.loads(info)
        #checking the API repsonse
        if '100' in info:
            obj = CableRecharge.objects.create(
                user = user,
                ordernumber = ordernumber,
                smart_no = smart_no,
                phone = phone,
                sub_amount = int(cable_amount)/100,
                customernumber = customer_number,
                customername = customer_name,
                billtype = billtype,
                messageresp = resp['message'],
                invoice = invoice,
                exchange_reference = resp['exchangeReference']
            )
            return render(request, 'airtime/successful_recharge_card.html')
        else:
            obj = CableRecharge.objects.create(
                user = user,
                ordernumber = ordernumber,
                smart_no = smart_no,
                phone = phone,
                sub_amount = int(cable_amount)/100,
                customernumber = customer_number,
                customername = customer_name,
                billtype = billtype,
                messageresp = "Failed",
                invoice = invoice,
                #exchange_reference = resp['exchangeReference']
            )
            return render(request, 'paystack/failure.html')
    else:
        return render(request, 'paystack/failure.html')