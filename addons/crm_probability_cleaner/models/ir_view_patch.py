from odoo import SUPERUSER_ID
import logging
from lxml import etree
import re

_logger = logging.getLogger(__name__)


def remove_probability_from_views(env):
    """
    Post-init hook for Odoo 17:
    1. Dynamically remove probability, tag_ids, and priority fields from base views.
    2. Remove inheritance records that fail due to missing fields.
    """

    # Fields we are cleaning up from the base views
    fields_to_clean = ['probability', 'tag_ids', 'priority']

    # Target models for base view patching
    target_models = ['crm.lead', 'crm.phonecall']

    _logger.info("crm_probability_cleaner: Starting view cleanup for fields: %s", fields_to_clean)

    # --- STEP 1: Patch Base Views (Removal of field elements) ---
    # Search for views of the target models that contain ANY of the target elements
    search_domain_arch = [('arch_db', 'ilike', f) for f in fields_to_clean]
    views_to_patch = env['ir.ui.view'].sudo().search([
                                                         ('model', 'in', target_models),
                                                     ] + [('arch_db', 'ilike', f) for f in
                                                          fields_to_clean])  # Add the ILIKE conditions

    _logger.info("crm_probability_cleaner: Found %d base view(s) to patch.", len(views_to_patch))

    for view in views_to_patch:
        arch = view.arch_db or ''
        changed = False

        try:
            doc = etree.fromstring(arch.encode('utf-8'))

            # Use XPath to find and remove elements by name
            for field_name in fields_to_clean:
                # Target field elements and associated labels/containers
                xpath_expression = (
                    f"//field[@name='{field_name}'] | "
                    f"//label[@for='{field_name}']"
                )

                # Special case: Probability header div
                if field_name == 'probability':
                    xpath_expression += " | //div[contains(@class, 'probability')]"
                # Special case: Priority widgets/divs
                if field_name == 'priority':
                    xpath_expression += " | //div[contains(@class, 'o_priority')] | //field[@widget='priority']"

                elements = doc.xpath(xpath_expression)

                for el in elements:
                    parent = el.getparent()
                    if parent is not None:
                        # Only remove if not the root node (safety check)
                        if parent.tag != doc.tag:
                            parent.remove(el)
                            changed = True
                        else:
                            # If element is at root level (rare), just remove the element itself
                            el.getparent().remove(el)
                            changed = True

            if changed:
                new_arch = etree.tostring(doc, encoding='unicode')
                # Odoo sometimes serializes boolean attributes as 'True'/'False'. Standardize.
                new_arch = new_arch.replace('="True"', '="1"').replace('="False"', '="0"')

                # IMPORTANT: Use preserve_view=True to prevent view re-computation until the module finishes
                view.with_context(preserve_view=True).write({'arch_db': new_arch})
                _logger.info("crm_probability_cleaner: Patched view ID %s (%s)", view.id, view.name)
        except Exception as e:
            _logger.error("crm_probability_cleaner: Error patching view %s (%s): %s", view.id, view.name, str(e))

    # --- STEP 2: Remove Failing Inheritance Records (The fix for your error) ---
    # Find inheritance records that modify the fields we just removed.
    # We search in the 'arch_db' column of ir.ui.view where 'inherit_id' is set (meaning it's an inheritance view).

    # We only care about inheritance views related to crm.lead or crm.phonecall
    # The xpath search is necessary because the inheritance specs are stored as XML strings.

    # Build a search condition for the inheritance specs
    inheritance_conditions = []
    for field_name in fields_to_clean:
        # Search for XML that tries to locate the field (e.g., <field name="priority"...)
        inheritance_conditions.append(('arch_db', 'ilike', f'<field name="{field_name}"'))

    # Final domain: Must be an inheritance view AND must target one of our fields
    domain = [('inherit_id', '!=', False)] + inheritance_conditions

    failing_inheritance_views = env['ir.ui.view'].sudo().search(domain)

    if failing_inheritance_views:
        _logger.warning(
            "crm_probability_cleaner: Found %d potentially failing inheritance views. Unlinking them to prevent 'Element not located' errors.",
            len(failing_inheritance_views))

        # Unlink (delete) the records
        failing_inheritance_views.unlink()
        _logger.info("crm_probability_cleaner: Successfully unlinked failing inheritance views.")

    _logger.info("crm_probability_cleaner: View cleanup complete.")

    # Re-trigger view re-computation
    env['ir.ui.view'].with_context(active_test=False)._post_load()

    return