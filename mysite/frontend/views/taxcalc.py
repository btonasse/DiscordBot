from django.shortcuts import render

def taxcalc(request):
    if request.method == 'POST':
        tax = {'gross_amt': None, 'net_amt': None, 'tax_rate': None, 'tax_amt': None}
        not_populated = 0
        errors = []
        for key in tax.keys():
            if request.POST.get(key):
                try:
                    tax[key] = float(request.POST.get(key))
                except ValueError:
                    errors.append(f'"{request.POST.get(key)}" is not a valid value for field "{key.capitalize()}".')
                    continue
                if key == 'rate' and (tax[key] < 0 or tax[key] > 100):
                    errors.append('Tax rate: enter a number between 0 and 100.')
            else:
                not_populated += 1
        if not_populated != 2:
            errors.append('Two - and only two - fields must be populated.')

        try:
            tax_dict = tax_calc(tax)
        except Exception as err:
            tax_dict = request.POST.dict()
            errors.append(str(err))
        context = {
            'tax_dict': tax_dict,
            'request_form': request.POST.dict(),
            'errs': errors
        }
    else:
        context = {
            'tax_dict': {'gross_amt': "", 'net_amt': "", 'tax_rate': "", 'tax_amt': ""},
            'request_form': {'gross_amt': "", 'net_amt': "", 'tax_rate': "", 'tax_amt': ""},
            'errors': []
        }
    return render(request, 'frontend/taxcalc/taxcalc.html', context)

# just for testing
def tax_calc(tax: dict):
	'''
	Calculates tax (VAT) based off of a combination of two variables: gross_amt, net_amt, rate or tax amount. Selecting rate+tax_amt can cause rounding errors.
	'''
	if sum([arg != None for arg in tax.values()]) != 2: #Validate that only two arguments were passed.
		raise ValueError("Tax_calc requires exactly two arguments.")
	try:
		for key, value in tax.items(): #Converts potential strings to float and validates that only numbers were passed
			if value is not None:
				tax[key] = float(value)
	except ValueError:
		raise ValueError("Only numbers are accepted as arguments.")

	if tax['gross_amt'] is not None:
		if tax['tax_rate'] is not None:
			try:
				tax['net_amt'] = tax['gross_amt']/(1+tax['tax_rate']/100)
			except ZeroDivisionError:
				if tax['gross_amt'] == 0:
					raise ZeroDivisionError(f'Cannot determine net amount from gross when rate is -100%.')
				else:
					raise ZeroDivisionError('Invalid gross amount for rate -100%.')
			tax['tax_amt'] = tax['gross_amt'] - tax['net_amt']
		elif tax['net_amt'] is not None:
			try:
				tax['tax_rate'] = (tax['gross_amt']/tax['net_amt']-1)*100
			except ZeroDivisionError:
				if tax['gross_amt'] == 0:
					tax['tax_rate'] = 0
				else:
					raise ZeroDivisionError(f"Gross amount {tax['gross_amt']} is not valid when net is 0.")
			tax['tax_amt'] = tax['gross_amt'] - tax['net_amt']
		else:
			tax['net_amt'] = tax['gross_amt'] - tax['tax_amt']
			try:
				tax['tax_rate'] = (tax['gross_amt']/tax['net_amt']-1)*100
			except ZeroDivisionError:
				raise ValueError(f"Gross and tax amount cannot be equal.")

	elif tax['net_amt'] is not None:
		if tax['tax_rate'] is not None:
			tax['gross_amt'] = tax['net_amt'] * (1+tax['tax_rate']/100)
			tax['tax_amt'] = tax['gross_amt'] - tax['net_amt']
		elif tax['tax_amt'] is not None:
			tax['gross_amt'] = tax['net_amt'] + tax['tax_amt']
			try:
				tax['tax_rate'] = tax['tax_amt']/tax['net_amt']*100 
			except ZeroDivisionError:
				if tax['tax_amt'] == 0:
					tax['tax_rate'] = 0
				else:
					raise ZeroDivisionError(f"Tax amount {tax['tax_amt']} is not valid when net is 0.")

	else:
		try:
			tax['gross_amt'] = tax['tax_amt']/(tax['tax_rate']/100) + tax['tax_amt']
			tax['net_amt'] = tax['gross_amt'] - tax['tax_amt']
		except ZeroDivisionError:
			if tax['tax_amt'] == 0:
				tax['gross_amt'] = 0
				tax['net_amt'] = 0
			else:
				raise ZeroDivisionError(f"Tax amount {tax['tax_amt']} is not valid when rate is 0.")
	
	for key, value in tax.items(): #Round final values
		tax[key] = round(value, 2)

	return tax