from django.urls import path
from . import views

app_name = 'circulation'

urlpatterns = [
    path('my-loans/', views.MyLoansView.as_view(), name='my_loans'),
    path('my-reservations/', views.MyReservationsView.as_view(), name='my_reservations'),
    path('reserve/<int:book_id>/', views.ReserveBookView.as_view(), name='reserve_book'),
    path('renew/<int:loan_id>/', views.RenewLoanView.as_view(), name='renew_loan'),
    path('fines/', views.MyFinesView.as_view(), name='my_fines'),
]

