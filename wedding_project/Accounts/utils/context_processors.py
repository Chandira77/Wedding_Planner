from django.contrib.auth.decorators import login_required

def user_role(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            dashboard_url = "admin"
        elif hasattr(request.user, "seller_dashboard"):
            dashboard_url = "seller_dashboard"
        elif hasattr(request.user, "guest"):
            dashboard_url = "guest_dashboard"
        else:
            dashboard_url = "user_dashboard"
    else:
        dashboard_url = None

    return {"dashboard_url": dashboard_url}
