# Week 3 Summary - Roles, Organizations and Request Ownership
My notes for the third week. I did all the tasks. The parts i assumed and my questions are at the end.

## 1. The Confirmed Roles
I replaced my old role names with the five you sent:

```python
class Roles(models.TextChoices):
    REPRESENTATIVE = "REPRESENTATIVE", "Representative"
    DIRECTORATE_STAFF = "DIRECTORATE_STAFF", "Directorate Staff"
    UNIT_STAFF = "UNIT_STAFF", "Unit Staff"
    COORDINATOR = "COORDINATOR", "Coordinator"
    DIRECTOR = "DIRECTOR", "Director"
```

Last week i had taken the names from the template folders, so this was the part i wasnt sure about and now its fixed.

## 2. Organization and Unit
I put both of them in `apps/core/models.py` because more than one app is going to use them and core is for the shared code.

```python
class Organization(models.Model):
    class OrgType(models.TextChoices):
        CLUB = "CLUB", "Club"
        SOCIETY = "SOCIETY", "Society"

    name = models.CharField(max_length=255, unique=True)
    org_type = models.CharField(max_length=20, choices=OrgType.choices)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Unit(models.Model):
    class UnitType(models.TextChoices):
        ALUMNI = "ALUMNI", "Alumni"
        SPORTS = "SPORTS", "Sports"
        CAREER = "CAREER", "Career"

    name = models.CharField(max_length=255, unique=True)
    unit_type = models.CharField(max_length=20, choices=UnitType.choices)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

I kept club and society in one table with a type field instead of two seperate models. When i looked at `staff/view_requests.html` the demo data already had an `orgType: "club"` field and the page has one filter for clubs and one for societies, so i think this is how the frontend expects it.

Both of them are registered in the admin so we can create them from there.

## 3. The Relationships
On the user:

```python
organization = models.ForeignKey("core.Organization", on_delete=models.PROTECT,
                                 null=True, blank=True, related_name="representatives")
unit = models.ForeignKey("core.Unit", on_delete=models.PROTECT,
                         null=True, blank=True, related_name="staff_members")
```

Both are `null=True` because a representative only has an organization and a unit staff only has a unit, so one of them is always empty.

`ActivityRequest` has the same two fields, and the view fills them from the user who is creating the request:

```python
activity_request.created_by = request.user
activity_request.organization = request.user.organization
activity_request.unit = request.user.unit
```

This way nobody can send a request for another club, because the user doesnt choose the club in the form.

## 4. Role Based Access
`login_required` only checks if you are logged in like you said, so i wrote a small decorator in `apps/core/decorators.py`:

```python
def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.role not in allowed_roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
```

Then every view in `apps/core/views.py` got the roles that are allowed to open it:

```python
@login_required
@role_required(User.Roles.DIRECTOR)
def director_dashboard(request):
    return render(request, "director/dashboard.html")
```

The order matters, `login_required` has to be on top. If its the other way around the user is not logged in yet and reading `request.user.role` gives an error.

I tested it with a representative account, `/director/dashboard/` and `/staff/dashboard/` both give 403 now.

## 5. Request Ownership
The `requests_app` list was loading everything like you said. Now:

```python
requests = ActivityRequest.objects.select_related("created_by", "organization", "unit")
if request.user.role == User.Roles.REPRESENTATIVE:
    requests = requests.filter(created_by=request.user)
```

For the URL part i put the rule on the model instead of the view, because the detail page, the edit page and the tests all need the same rule:

```python
def can_be_seen_by(self, user):
    if user.role == "REPRESENTATIVE":
        return self.created_by_id == user.id
    return True
```

The detail view calls it and raises `PermissionDenied` if it returns False. I tried it by changing the number in the address to another users request and it gives 403.

## 6. Request Detail Page
New page at `/requests/<id>/`. It shows the title, description, dates, participants, status, who submitted it, the organization or unit, and the created and last updated times. The titles in both list pages are links to it now.

## 7. Editing
Same idea as above, the rule is on the model:

```python
def can_be_edited_by(self, user):
    return self.created_by_id == user.id and self.status == self.Status.DRAFT
```

So only the creator can edit and only while its still a draft. The edit view uses the same ModelForm with `instance=activity_request`, which fills the form with the current values and writes over the same row instead of creating a new one.

The Edit button on the detail page only shows up if you are allowed to edit, but the check is in the view too, not only in the template.

I tested a pending request and it gives 403.

## 8. Superuser
The old one only used `setdefault`, so if someone passed `is_staff=False` it stayed False and we would have a superuser that cant open the admin. Now it raises an error instead:

```python
def create_superuser(self, email, password=None, **extra_fields):
    extra_fields.setdefault("is_staff", True)
    extra_fields.setdefault("is_superuser", True)
    extra_fields.setdefault("role", User.Roles.DIRECTOR)

    if extra_fields.get("is_staff") is not True:
        raise ValueError("Superuser must have is_staff=True.")
    if extra_fields.get("is_superuser") is not True:
        raise ValueError("Superuser must have is_superuser=True.")

    return self.create_user(email, password, **extra_fields)
```

I also gave it a default role, because before that the superuser had an empty role and the `role_required` decorator would not know what to do with it. I used `DIRECTOR` since thats the widest one, but if you want a different one its easy to change.

## 9. Tests
24 tests now, all passing with `python manage.py test apps.requests_app`. The 7 from last week still pass and i added 17:

- role based access, 4 tests (representative cannot open the staff and director pages, unit staff cannot open the coordinator page, and a representative can open its own dashboard)
- organization and unit relationships, 3 tests (a representative has an organization and no unit, a unit staff has a unit and no organization, and a new request gets the organization of the creator)
- ownership, 4 tests (a representative only sees its own requests, a director sees all of them, opening another users request gives 403, opening your own works)
- editing, 3 tests (the creator can edit a draft, a pending request gives 403, another users request gives 403)
- superuser, 3 tests (the flags and the role are set, and it raises an error when `is_staff=False` or `is_superuser=False`)

## What i assumed
These are the three things i had to decide by myself. Please tell me if any of them is wrong, they are all easy to change.

- **Unit Staff uses the Directorate Staff pages.** There is no template folder for it, there are only representative, staff, coordinator and director. So i let both staff roles open the same pages.
- **A representative only sees its own requests, not all the requests of its organization.** The page says "My Activity Requests" so i went with the narrow one. If a club can have more than one representative account this probably needs to change.
- **Coordinator and Director are not connected to a unit or an organization**, they see all the requests. Also the director folder has no `manage_users.html` so i didnt give that role to them.

## What i left out

- **The sidebar still shows all four role sections to everybody.** Its written directly in `base.html` and it wasnt in this weeks list, so i didnt touch it. The links are not a security problem because they give 403, but it looks strange for a representative to see the director menu.
- **Nothing stops a user from having an organization and a unit at the same time.** Right now this is only handled by us being careful in the admin. You said last week that some rules will need to be at the model level later, i think this is one of them.
- **The 8 step wizard** is still not connected, like we agreed.
- **Alumni, Sports and Career dont appear anywhere in the frontend.** I searched all the templates and the pages only talk about clubs and societies, so i dont know yet where the units are going to be shown.

## Questions

1. Is the Unit Staff assumption ok, or will there be seperate pages for it later?
2. Can one organization have more than one representative account? That changes what a representative should see in the list.


## Corrections after review
These are the changes i made after your feedback on this PR.

- **Request views are explicit by role now.** `create_request` and `edit_request` only let Representative and Unit Staff in. The list and the detail page still let every role in, but what you see is decided per role.
- **`can_be_seen_by` lists every role one by one.** Representative sees its own requests, Unit Staff sees only the requests of its own unit, Directorate Staff, Coordinator and Director see all of them. Any role that is not in the list gets `False`, so a new role doesnt get access by accident. The list page uses the same rules.
- **Unit Staff is scoped to its own unit.** It can still open the shared staff dashboard and request pages, but it cant open `manage_users` anymore, only Directorate Staff can. I thought managing all users doesnt fit a unit scoped role, please tell me if thats wrong.
- **Superusers dont get the Director role anymore.** The `role` field can be empty now and the superuser keeps it empty, admin access comes only from `is_superuser` and `is_staff`.
- **Invalid user assignments are blocked** in `User.clean()`. A Representative needs an organization and no unit, a Unit Staff needs a unit and no organization, and the other roles cant have either one. A normal user without a role is also blocked, only a superuser can have an empty role.
- **Tests.** 42 tests now, all passing. I added tests for the create and edit pages per role, unit scoping, the user validation and the superuser role. For the validation tests i check which field the error is on, because at first they were passing only because the test users had no password, not because of my rule.