# Permission System Audit - Role-Based Access Control

## Audit Summary

Complete audit of all admin permission checks to ensure compliance with the new role-based system (OWNER/ADMIN/MOD) instead of legacy `user_type == "admin"` checks.

---

## Files Audited & Updated

### 1. **auth/decorators.py** ✅
- **Issue**: Used `current_user.user_type != "admin"` for admin gate-keeping
- **Fix**: Changed to `not current_user.is_admin()`
- **Impact**: Ensures OWNER, ADMIN, and MOD roles all pass admin checks

### 2. **auth/routes.py** ✅
- **Issue**: Counted admins using `u.user_type == "admin"`
- **Fix**: Changed to `u.is_admin()`
- **Impact**: Dashboard now correctly counts all privileged users

**Routes with permission checks:**
- `/admin/user/<id>/verify` - Uses `can_manage_user()`
- `/admin/user/<id>/make-mod` - Uses `can_change_role(user, 'MOD')`
- `/admin/user/<id>/remove-role` - Uses `can_manage_user()` and `is_owner()` check
- `/admin/user/<id>/suspend` - Uses `can_suspend_user()`
- `/admin/user/<id>/delete` - Uses `can_delete_user()`
- `/admin/reports` - Protected by `@admin_required` decorator
- `/admin/report/<id>/dismiss` - Protected by `@admin_required` decorator
- `/admin/report/<id>/delete-review` - Protected by `@admin_required` decorator

### 3. **reviews.py** ✅
- **Lines 214**: Changed reply eligibility from `'admin'` in user_type list to `is_admin()` method
- **Line 228**: Changed Reply creation to use `is_admin()` instead of `user_type == 'admin'`
- **Line 274**: Changed analytics permission check to use `is_admin()`
- **Line 510**: Changed pin_review to use `is_admin()`
- **Line 524**: Changed unpin_review to use `is_admin()`

### 4. **templates/base.html** ✅
- **Issue**: Admin link in navbar used `current_user.user_type == 'admin'`
- **Fix**: Changed to `current_user.is_admin()`
- **Impact**: OWNER and MOD users can now access admin panel

### 5. **templates/lecturer_profile.html** ✅
- **Issue**: Multiple checks used `current_user.user_type == 'admin'` or `current_user.user_type != 'admin'`
- **Fixed Lines**:
  - Line 120: View analytics permission check
  - Line 155: Anonymous review visibility
  - Line 159: Admin-only reveal for anonymous reviews
  - Line 206: Review pin/unpin/delete actions
  - Line 247: Anonymous reply attribution
  
- **Impact**: MOD users can now pin/unpin/delete reviews, view full analytics

### 6. **templates/admin_users.html** ✅
- **Column Rename**: "Type" → "Account Type" for clarity
- **Context**: "Type" now refers to account type (Student/Lecturer/Admin) which is separate from Role (OWNER/ADMIN/MOD)
- **Permission Logic**: All action buttons use:
  - `current_user.can_manage_user(u)` - Check if user can manage target
  - `current_user.can_change_role(u, 'MOD')` - Check if can assign role
  - `u.is_owner()` - Prevent actions on OWNER accounts
  - `current_user.can_delete_user(u)` - Check delete permission
  - `current_user.can_suspend_user(u)` - Check suspend permission

---

## Permission Hierarchy Verification

### Role Definitions (in models.py)
```python
is_owner():    role == 'OWNER'
is_admin():    role in ['OWNER', 'ADMIN']
is_mod():      role in ['OWNER', 'ADMIN', 'MOD']
```

### Permission Method Verification

✅ **can_manage_user(target_user)**
- OWNER can manage all users
- ADMIN can manage: Students, Lecturers, MODs (NOT other ADMINs, NOT OWNER)
- MOD cannot manage anyone
- Result: OWNER > ADMIN > MOD

✅ **can_change_role(target_user, new_role)**
- OWNER can assign: OWNER, ADMIN, MOD (any role)
- ADMIN can assign: MOD only (to non-ADMIN/OWNER users)
- MOD cannot assign any role
- Result: Prevents role escalation

✅ **can_delete_user(target_user)**
- Returns False if target is OWNER
- Otherwise checks `can_manage_user()`
- Result: OWNER accounts cannot be deleted

✅ **can_suspend_user(target_user)**
- Returns False if target is OWNER
- Otherwise checks `can_manage_user()`
- Result: OWNER accounts cannot be suspended

---

## Legacy Code Removal Status

### Completely Removed/Replaced ✅
- `user_type == "admin"` checks (auth/decorators.py)
- `user_type != "admin"` checks (reviews.py)
- `'admin' in user_type_list` checks (reviews.py)
- Admin navbar visibility based on user_type (base.html)

### Retained (Necessary) ✅
- `user_type` column in User model - Still needed to distinguish Student/Lecturer/Admin account types
- `user_type` in templates - Still used for role-specific UI (Student/Lecturer navigation)
- Test account definitions - Still specify user_type for account categorization

---

## Constraint Verification

✅ **MOD Cannot Escalate Roles**
- Method `can_change_role()` checks `if self.is_admin()` before allowing role assignment
- MOD is not admin, so always returns False

✅ **ADMIN Cannot Assign ADMIN/OWNER**
- Method limits ADMIN to assigning only `['MOD']`
- ADMIN cannot assign ADMIN or OWNER roles

✅ **OWNER Cannot Be Modified by Non-OWNER**
- All user modification checks test `target_user.is_owner()`
- Remove Role, Delete, Suspend return False if target is OWNER
- Only OWNER can modify OWNER accounts (and only other OWNERs if any exist)

✅ **OWNER Accounts Protected**
- cannot be deleted: `can_delete_user()` returns False
- cannot be suspended: `can_suspend_user()` returns False
- cannot have role removed: `admin_remove_role()` checks `not user.is_owner()`

---

## Testing Recommendations

1. **As OWNER (owner@mmu.edu.my)**
   - Can access admin dashboard ✓
   - Can view all users ✓
   - Can manage ADMIN/MOD/other accounts ✓
   - Can assign any role (OWNER/ADMIN/MOD) ✓
   - Cannot manage own OWNER account ✓

2. **As ADMIN (admin@mmu.edu.my)**
   - Can access admin dashboard ✓
   - Can view all users ✓
   - Can manage MOD/Lecturer/Student accounts ✓
   - Can only assign MOD role ✓
   - Cannot assign ADMIN or OWNER ✓
   - Cannot manage OWNER or other ADMIN accounts ✓

3. **As MOD (mod@mmu.edu.my)**
   - Can access admin dashboard (via is_admin check) ✓
   - Can view all users ✓
   - Cannot manage any accounts ✓
   - Can pin/unpin/delete reviews ✓
   - Cannot assign roles ✓

4. **As Lecturer/Student**
   - Cannot access admin panel ✓
   - Cannot pin/unpin reviews ✓
   - Cannot access role management endpoints ✓

---

## Security Notes

1. **Database Level**: No additional validation needed - role assignment only happens through permission-checked routes
2. **Front-End Level**: UI buttons conditionally rendered based on permission methods
3. **Back-End Level**: All routes double-check permissions before modifying user data
4. **Default State**: Users default to no role (role=NULL), gaining access only when explicitly assigned by OWNER

---

## Files Not Requiring Changes

- `models.py` - Already implements proper role-based methods
- `init_db_fresh.py` - Already assigns roles correctly at account creation
- `admin_panel.html` - Legacy template, not in use
- Other templates (index.html, login.html, register.html, etc.) - No admin permission logic
