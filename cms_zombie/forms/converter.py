import re

class FormConverter:
    """Converts legacy PHP form shortcodes (Contact Form 7, Gravity Forms)
    into accessible, modern serverless form component markup.
    """

    FORM_SHORTCODE_RE = re.compile(r"\[(?:contact-form-7|gravityform|wpforms)[^\]]*\]", re.IGNORECASE)

    MODERN_FORM_HTML = """
<div class="cms-zombie-form-container my-8 p-6 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl">
  <h3 class="text-xl font-bold mb-4">Send a Message</h3>
  <form action="https://formspree.io/f/your-form-id" method="POST" class="space-y-4">
    <div>
      <label for="name" class="block text-sm font-medium mb-1">Your Name</label>
      <input type="text" id="name" name="name" required class="w-full px-3 py-2 border rounded-md" />
    </div>
    <div>
      <label for="email" class="block text-sm font-medium mb-1">Your Email</label>
      <input type="email" id="email" name="email" required class="w-full px-3 py-2 border rounded-md" />
    </div>
    <div>
      <label for="message" class="block text-sm font-medium mb-1">Message</label>
      <textarea id="message" name="message" rows="4" required class="w-full px-3 py-2 border rounded-md"></textarea>
    </div>
    <button type="submit" class="px-5 py-2.5 bg-emerald-600 text-white font-medium rounded-md hover:bg-emerald-700 transition">
      Submit Message
    </button>
  </form>
</div>
"""

    @classmethod
    def convert_forms(cls, content: str) -> str:
        """Replaces legacy form shortcodes with the modern serverless form component."""
        if not content:
            return ""
        return cls.FORM_SHORTCODE_RE.sub(cls.MODERN_FORM_HTML.strip(), content)
