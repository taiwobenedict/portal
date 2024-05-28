from django import template
from django.db.models import Q
from django.utils import timezone
import datetime
from django.utils.html import format_html
from monnify_app.models import MonnifyAccount
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def format_banks(id):
	user_bank = MonnifyAccount.objects.filter(user__id=id)
	if user_bank.exists():
		user_bank = user_bank.first()
		num_of_acc = user_bank.accountNumber.split("|")
		num_of_banks = user_bank.bankName.split("|")
		num_of_bankcode = user_bank.bankCode.split("|")
		res = []
		if len(num_of_banks) > 1:
			for i in range(0, len(num_of_banks)):
				res.append(f"""<div class="col-md-12 col-lg-6">
					Account Number:{num_of_acc[i]}<br/>
					Bank Name:{num_of_banks[i]}<br/>
					Bank Code:{num_of_bankcode[i]}
				<hr/></div>""")
		return  mark_safe('<div class="row">' + "".join(res) + '</div>')
	else:
		pass
