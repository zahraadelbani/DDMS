# Week 4 Summary - Role Based Permissions, Sidebar and Redirects
My notes for the fourth week. I did all 5 tasks. The parts i assumed and the things i noticed are at the end.

## 1. Role Based Request Permissions
Most of this was already done in the Week 3 corrections (PR #3), so this week i mostly checked it and added more tests. Just to have it in one place, this is how it works now:

- **Create and edit** - only Representative and Unit Staff can open them. They are protected with `role_required` on top of `login_required`.
- **List and detail** - every role can open the page, but what you see is decided per role in `can_be_seen_by()` and in the list view.
- **Edit** - only the creator, and only while the request is still a draft.

Every role is written one by one and a role that is not in the list gets nothing, so a new role doesnt get access by accident.

## 2. Unit Staff Scoping
Also from the Week 3 corrections. Unit Staff only sees and opens the requests of its own unit:

```python
if user.role == User.Roles.UNIT_STAFF:
    return self.unit_id is not None and self.unit_id == user.unit_id
```

The `unit_id is not None` part is there because if both are empty, `None == None` would be True and a unit staff without a unit could see requests without a unit.

This week i added tests for the edit side too, a unit staff cannot edit a request of another unit but can edit its own draft.

## 3. Sidebar
Before this week everybody saw all four role sections in the left menu. Now every section in `templates/base.html` is wrapped with the role that owns it:

```html
{% if user.role == "DIRECTOR" %}
<div class="sidebar-nav-section">
    <p class="sidebar-nav-label">Director</p>
    ...
</div>
{% endif %}
```

- Representative, Coordinator and Director only see their own section.
- The Staff section is shown to both Directorate Staff and Unit Staff since they share the pages, but the **Manage Users** link inside it is only shown to Directorate Staff.
- The **All** section (Profile and Logout) stays for everybody.

This is only the visual part. The real protection is still `role_required` in the views, so even if someone types the address of a page they dont see in the menu they still get 403.

While doing this i also noticed the Logout icon was missing. There was a placeholder text in the svg from week 2 instead of the real icon, so i put the real one back.

## 4. Role Based Redirects After Login
Before this everybody went to the profile page after login. Now `DDMSLoginView` in `apps/accounts/views.py` sends each role to its own dashboard:

```python
DASHBOARD_BY_ROLE = {
    User.Roles.REPRESENTATIVE: "core:representative_dashboard",
    User.Roles.DIRECTORATE_STAFF: "core:staff_dashboard",
    User.Roles.UNIT_STAFF: "core:staff_dashboard",
    User.Roles.COORDINATOR: "core:coordinator_dashboard",
    User.Roles.DIRECTOR: "core:director_dashboard",
}


def get_success_url(self):
    next_url = self.get_redirect_url()
    if next_url:
        return next_url

    user = self.request.user
    if user.role in DASHBOARD_BY_ROLE:
        return reverse(DASHBOARD_BY_ROLE[user.role])
    if user.is_superuser:
        return reverse("admin:index")
    return reverse("core:profile")
```

The order is on purpose. If the user was trying to open a page before logging in (`?next=...`), they still go back to that page first, i didnt want to break that from week 2. `get_redirect_url()` is djangos own method and it also checks that `next` is a safe address on our site.

## 5. Tests
57 tests now, all passing with `python manage.py test apps.requests_app`. The 42 from before still pass and i added 15 in `apps/requests_app/tests/test_week4.py`:

- **cross role access** - a table of which roles can open which page, and one test that tries all 5 roles on all 11 dashboard pages (55 combinations) and expects 200 or 403. I used `subTest` so if one fails it shows which role and which page. Also every role can open profile, unit staff cannot edit another units request but can edit its own, and coordinator, director and directorate staff can open any request.
- **unauthorized URL access** - a logged out user is sent to login from every page, a request that doesnt exist gives 404, and posting to another users edit page doesnt change the request. The last one was new for me, until now we only tested opening the page (GET) and not actually saving (POST).
- **sidebar** - each role only sees its own section, unit staff doesnt see Manage Users, directorate staff does.
- **login redirects** - every role goes to its own dashboard, `next` still wins over the dashboard, and a superuser goes to the admin.

For the sidebar tests i had to cut only the `<nav>` part out of the page and check that. At first i checked the whole page and the unit staff test failed, because the staff dashboard page itself has a Manage Users button in the content (see below).

## What i assumed

- **Unit Staff goes to the staff dashboard after login.** You said Unit Staff will have its own unit scoped experience later, but right now there is no seperate page for it, so it lands on the shared staff dashboard.
- **A superuser without a role goes to the admin panel after login.** Since the superuser has no role anymore, it doesnt fit any dashboard, and the admin is where we use that account anyway.

## Things i noticed but didnt change

- **The staff dashboard page has its own "Manage Users" button in the content**, not in the sidebar. It is part of the design so Unit Staff also sees it. If they click it they get 403 so its not a security problem, but it can be confusing. I didnt change it because the page content was not part of this weeks tasks.
- **The dashboard pages still show the demo numbers and names** (for example "Pending your review 7" and "Amina Yusuf" on the profile page). They are still the static frontend, only the sidebar and the access around them changed.
- **The profile page still has the "Preview as role (dev)" dropdown.** I think it only changes what is shown on that page in the browser, it doesnt change the real role, so the sidebar and the access dont change with it. I left it because i thought the team might still be using it for the design.
- **This branch is based on the Week 3 corrections branch**, because PR #3 wasnt merged yet when i started. Once PR #3 is merged, only this weeks commits should show in this PR.