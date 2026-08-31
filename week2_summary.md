# Week 2 Summary - Authentication and Activity Requests
My notes for the second week. I did all 8 tasks. The parts i left out and my questions are at the end.

## 1. Custom User Model
I replaced the default django user with our own one in `apps/accounts/models.py`. It logs in with email instead of username and it has a `role` field like i wrote last week:

```python
class User(AbstractUser):
    class Roles(models.TextChoices):
        REPRESENTATIVE = "REPRESENTATIVE", "Club / Society Representative"
        COORDINATOR = "COORDINATOR", "Sports Affairs"
        DIRECTOR = "DIRECTOR", "Activity Directorate"
        STAFF = "STAFF", "Rectorate / Staff"

    username = None
    email = models.EmailField("email address", unique=True)
    role = models.CharField(max_length=25, choices=Roles.choices)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
```

`username = None` removes the field we dont use and `USERNAME_FIELD = "email"` tells django to look at the email when someone logs in.

I also had to write a small `UserManager`. The one django gives asks for a username so `createsuperuser` doesnt work without it. That was the part i didnt expect.

`AUTH_USER_MODEL = "accounts.User"` is in `config/settings/base.py` now, and i registered the model in `apps/accounts/admin.py` so we can open the accounts from the admin panel like we planned.

The role names are the same as the folders in `templates/accounts/`. I am still not sure about `coordinator`.

## 2. Login and Logout
I used djangos `LoginView` and `LogoutView` in `apps/accounts/views.py` with our own template, so the password checking and the session part is done by django and we dont write it.

The login page was html only, so i connected it to the view. I added `method="post"`, the action, `{% csrf_token %}` and made the button a submit button. I also changed the email field name to `username`, django looks for that name but it reads it as the email because of `USERNAME_FIELD`. And i added a small red box that shows when the email or password is wrong.

For logout i had to use a form with POST and not a link. Django 5 doesnt allow logout with GET anymore.

The `Sign in with Google`, `Security Key / Biometrics`, `Remember me` and `Forgot password` parts are still not connected, they were not in this weeks list.

## 3. Protecting the Dashboard Pages
I put `@login_required` on all the views in `apps/core/views.py`. If you are not logged in it sends you to the login page.

I also added `<input type="hidden" name="next" value="{{ next }}">` to the login form. Django puts the page you wanted in the address as `?next=...` and the form has to send it back, otherwise you always land on the profile page after login.

## 4. ActivityRequest Model
In `apps/requests_app/models.py` with the fields from the task:

```python
class ActivityRequest(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    expected_participants = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="activity_requests"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

I used `PROTECT` on `created_by` like i said last week so a user cannot be deleted while their requests are still there.

Last week my draft had six statuses but `PENDING_DIRECTOR` and `PENDING_RECTORATE` belong to the approval chain, so i kept only four for now.

## 5. The Form
`ActivityRequestForm` is a ModelForm in `apps/requests_app/forms.py`. `status` and `created_by` are not in the form fields, the view fills them:

```python
activity_request = form.save(commit=False)
activity_request.created_by = request.user
activity_request.save()
```

`commit=False` gives you the object without writing it to the database yet, so i can put `created_by` on it first and then save. Status is not touched because the model already has the default.

The page is at `/requests/new/`.

## 6. The Request List
`/representative/view_requests/` reads from the database now. The demo javascript array is replaced with a django `for` loop.

The filter buttons were javascript before, now they are links like `?status=pending` and the filtering happens in the view. I hope this is what was meant by reading from the database, if you wanted to keep the javascript side i can do it that way too.

The list only shows the requests of the user who is logged in, so a club sees its own requests and can follow them when they are approved or rejected.

## 7. Validation
Both rules are in the form:

```python
def clean_expected_participants(self):
    participants = self.cleaned_data["expected_participants"]
    if participants < 1:
        raise forms.ValidationError("Expected participants must be greater than 0.")
    return participants

def clean(self):
    cleaned_data = super().clean()
    start_date = cleaned_data.get("start_date")
    end_date = cleaned_data.get("end_date")
    if start_date and end_date and end_date <= start_date:
        raise forms.ValidationError("End date must be after the start date.")
    return cleaned_data
```

The date one has to be in `clean()` and not in a seperate field method, because it compares two fields and both of them need to be ready first. That was new for me.

## 8. Tests
7 tests in `apps/requests_app/tests/test_requests.py`, they all pass with `python manage.py test apps.requests_app`:

- login with the correct password
- login with a wrong password
- the list page sends you away when you are not logged in
- creating a request saves it adn sets `created_by`
- a request with the end date before the start date is not saved
- a request with 0 participants is not saved
- the list page shows the request

## What i left out

- **The 8 step submit request page.** I didnt connect it. Its steps are Club Info, Services, Transport, Budget, Documents and Compliance, and most of those are the parts we should not do yet, so i thought it was better to leave the page as it is. Instead i made a simple form at `/requests/new/` with only the model fields. So there are two pages right now, the wizard which still saves nothing, and the simple one which saves.
- **The approval timeline column and the rejection reason popup** on the list page. Both need the approval steps so i took them out for now and put Start and Participants in that space.
- **Editing a request.** There is no edit page yet, it was not in this weeks list. The model has an `updated_at` field already so it keeps the last change time when we add it later.
- **The `.env` values.** I wasnt sure if they are supposed to be loaded already. `development.py` reads them with `os.getenv` but i couldnt see a package like `python-dotenv` in requirements, so i think the defaults in `base.py` are being used. It didnt cause me any problem locally so i left it as it is.

## Questions

1. After login everyone goes to the profile page right now. From the meetings i understood that everyone should land on their own dashboard instead. I didnt change it because its about roles, but if you confirm it i can add it.
2. For the 8 step wizard, do we connect it step by step as the other models come, or does the simple form become the real one and the wizard goes away?