import logging
from lxml import etree

_logger = logging.getLogger(__name__)


# --- From crm_lead_code ---
def create_code_equal_to_id(env):
    _logger.info("Pre-init hook: Adding 'code' column to 'crm_lead' table.")
    env.cr.execute("ALTER TABLE crm_lead ADD COLUMN IF NOT EXISTS code character varying;")
    env.cr.execute("UPDATE crm_lead SET code = id WHERE code IS NULL;")
    _logger.info("Pre-init hook: Finished adding 'code' column.")


# --- From crm_lead_code ---
def assign_old_sequences(env):
    _logger.info("Post-init hook: Assigning sequential codes to existing leads.")
    sequence = env.ref('marketing_analysis_system.sequence_lead', raise_if_not_found=False)
    if not sequence:
        _logger.warning("Could not find 'sequence_lead'. Skipping sequence assignment.")
        return
    leads = env["crm.lead"].search([('code', 'ilike', '%New%')], order="id")
    for lead in leads:
        lead.code = sequence.next_by_id()
    _logger.info(f"Post-init hook: Assigned sequences to {len(leads)} leads.")


# --- From crm_phonecall_summary_predefined ---
def convert_names_to_many2one(env):
    _logger.info("Post-init hook: Migrating crm.phonecall 'name' to 'summary_id'.")
    summary_model = env["crm.phonecall.summary"]
    phonecall_model = env["crm.phonecall"]
    calls_to_migrate = phonecall_model.search([("summary_id", "=", False), ("name", "!=", False)])

    for call in calls_to_migrate:
        try:
            with env.cr.savepoint():
                summary = summary_model.search([("name", "=", call.name)], limit=1)
                if not summary:
                    summary = summary_model.create({"name": call.name})
                call.summary_id = summary.id
        except Exception as e:
            _logger.error(f"Could not migrate phonecall ID {call.id}: {e}")
    _logger.info(f"Post-init hook: Migrated {len(calls_to_migrate)} phonecall summaries.")


# --- From crm_probability_cleaner ---
def remove_probability_from_views(env):
    _logger.info("Post-init hook: Cleaning probability, tags, and priority from CRM views.")
    fields_to_clean = ['probability', 'tag_ids', 'priority']
    view_ids_to_clean = [
        'crm.crm_case_form_view_oppor',
        'crm.crm_case_tree_view_oppor',
        'crm.crm_case_kanban_view_leads',
        'crm_phonecall.crm_case_inbound_phone_tree_view',
        'crm_phonecall.crm_case_phone_form_view'
    ]

    for view_xml_id in view_ids_to_clean:
        try:
            view = env.ref(view_xml_id, raise_if_not_found=True)
            arch = etree.fromstring(view.arch)
            changed = False
            for field_name in fields_to_clean:
                for node in arch.xpath(f"//field[@name='{field_name}']"):
                    node.set('invisible', '1')
                    changed = True
            if changed:
                view.arch = etree.tostring(arch, encoding='unicode')
                _logger.info(f"Cleaned fields from view: {view.name} ({view.xml_id})")
        except Exception as e:
            _logger.warning(f"Could not clean view {view_xml_id}. It might not exist. Error: {e}")


# --- Main Hook Functions ---
def run_pre_init_hooks(env):
    _logger.info("Running pre-initialization hooks for marketing_analysis_system...")
    create_code_equal_to_id(env)
    _logger.info("Finished pre-initialization hooks.")


def run_post_init_hooks(env):
    _logger.info("Running post-initialization hooks for marketing_analysis_system...")
    assign_old_sequences(env)
    convert_names_to_many2one(env)
    remove_probability_from_views(env)  # Run this last
    _logger.info("Finished post-initialization hooks.")