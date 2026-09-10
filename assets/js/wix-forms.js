/* ============================================================
   WIX FORMS SUBMISSION
   ------------------------------------------------------------
   Submits enquiries to Wix Forms as an anonymous visitor.

   Deliberately inert until configured: with no clientId or no
   form id, submitWixForm() returns false and the caller keeps
   the existing mailto fallback. That lets this ship before the
   form exists in Wix without changing live behaviour.

   Docs:
     visitor token — POST https://www.wixapis.com/oauth2/token
                     { clientId, grantType: "anonymous" }
     submission    — POST https://www.wixapis.com/form-submission-service/v4/submissions

   Submission keys are each field's `target` from the form
   schema, NOT its GUID and NOT its label. Keep FIELD_TARGETS in
   step with scripts/wix-forms/*.form.json.
   ============================================================ */

/* Client ID comes from the destination site's Headless Settings
   → OAuth apps. The form ids come from CreateForm. Both are
   public values, safe to ship. */
const WIX_FORMS_CONFIG = {
  // Headless client "Jayguzmusicandevents_official_site" on Wix site
  // c6da36f6 (Jay's premium site). Verified 2026-09-10: issues anonymous
  // visitor tokens, HTTP 200. Public value — it is meant to ship here.
  clientId: '725f99c3-aa1e-4a85-979c-2a830714f8d5',
  forms: {
    // "Website - Event Consultation" on c6da36f6, created 2026-09-10
    consultation: 'f3eeeeec-4ab0-4f49-bb73-87075198c48f',
    'coordinator-inquiry': '',
    'song-request': '',
  },
};

/* HTML input name → Wix form field target. Anything not listed
   is dropped rather than guessed, so an unmapped field fails
   loudly in review instead of silently vanishing from a lead. */
const FIELD_TARGETS = {
  consultation: {
    email: 'email',
    phone: 'phone',
    'event-type': 'event_type',
    message: 'message',
  },
};

let visitorTokenPromise = null;

function getVisitorToken(clientId) {
  if (!visitorTokenPromise) {
    visitorTokenPromise = fetch('https://www.wixapis.com/oauth2/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ clientId: clientId, grantType: 'anonymous' }),
    })
      .then((res) => {
        if (!res.ok) throw new Error('token HTTP ' + res.status);
        return res.json();
      })
      .then((json) => json.access_token)
      .catch((err) => {
        visitorTokenPromise = null; // let the next attempt retry
        throw err;
      });
  }
  return visitorTokenPromise;
}

/* Build the submissions map. Empty values are omitted — Wix
   rejects a required field sent as "", and an optional field
   sent as "" stores a blank rather than nothing. */
function buildSubmissions(formName, data) {
  const targets = FIELD_TARGETS[formName];
  if (!targets) return null;

  const submissions = {};
  const unmapped = [];

  data.forEach((value, key) => {
    if (key === 'bot-field' || key === 'form-name') return;
    const target = targets[key];
    if (!target) {
      unmapped.push(key);
      return;
    }
    const trimmed = typeof value === 'string' ? value.trim() : value;
    if (trimmed !== '' && trimmed != null) submissions[target] = trimmed;
  });

  if (unmapped.length) {
    console.warn('[wix-forms] no target mapped for:', unmapped.join(', '));
  }
  return submissions;
}

/**
 * Submit one form to Wix Forms.
 * @returns {Promise<boolean>} true if Wix accepted the submission.
 *   false means "not configured" — the caller should fall back.
 *   Throws only when Wix was configured but the call failed, so a
 *   genuine outage still reaches the mailto path.
 */
async function submitWixForm(formName, data) {
  const clientId = WIX_FORMS_CONFIG.clientId;
  const formId = WIX_FORMS_CONFIG.forms[formName];
  if (!clientId || !formId) return false;

  const submissions = buildSubmissions(formName, data);
  if (!submissions) return false;

  const token = await getVisitorToken(clientId);

  const res = await fetch(
    'https://www.wixapis.com/form-submission-service/v4/submissions',
    {
      method: 'POST',
      headers: {
        Authorization: token,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        submission: { formId: formId, submissions: submissions },
      }),
    }
  );

  if (!res.ok) throw new Error('submission HTTP ' + res.status);
  return true;
}

window.submitWixForm = submitWixForm;
window.WIX_FORMS_CONFIG = WIX_FORMS_CONFIG;
