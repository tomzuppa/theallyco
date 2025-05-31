# -----------------------------------------
# 📄 TERMS & CONDITIONS STATIC PAGE
# -----------------------------------------
# 📄 Static view for Terms and Conditions
from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render

class TermsView(View):
    def get(self, request):
        # ✅ Adjusted template path to match actual file location
        return render(request, 'legal/terms.html')

