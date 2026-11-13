import { login, signup, handleAuthCallback, getUser } from 'https://esm.sh/@netlify/identity@2.0.1';
const show = (message, error = false) => {
  let status = document.getElementById('authStatus');
  if (!status) {
    status = document.createElement('p');
    status.id = 'authStatus'; status.setAttribute('role', 'status');
    document.querySelector('form')?.prepend(status);
  }
  if (status) { status.className = error ? 'alert alert-danger' : 'alert alert-info'; status.textContent = message; }
};
try {
  const callback = await handleAuthCallback();
  if (callback?.type === 'confirmation') location.replace('/dashboard/');
  else if (!callback && location.pathname === '/login/' && await getUser()) location.replace('/dashboard/');
  else if (callback?.type === 'recovery' || callback?.type === 'invite') show('Use the account recovery link sent by your administrator.');
} catch { show('The confirmation link has expired or is invalid. Please sign in or request another confirmation.', true); }
const form = document.querySelector('form[action="/login/"], form[action="/citizen/signup/"]');
if (form) {
  form.addEventListener('submit', async event => {
    event.preventDefault();
    const data = new FormData(form);
    const button = form.querySelector('button[type="submit"]');
    if (button) button.disabled = true;
    try {
      if (form.action.endsWith('/citizen/signup/')) {
        if (data.get('password') !== data.get('confirm_password')) throw new Error('Passwords do not match.');
        const user = await signup(String(data.get('email')), String(data.get('password')), { full_name: String(data.get('full_name')), phone_number: String(data.get('phone_number')) });
        if (user.emailVerified) location.replace('/dashboard/');
        else show('Account created. Check your email to confirm your account before signing in.');
      } else {
        await login(String(data.get('username')), String(data.get('password')));
        location.replace('/dashboard/');
      }
    } catch (error) { show(error.message || 'Unable to sign in. Please try again.', true); }
    finally { if (button) button.disabled = false; }
  });
}
