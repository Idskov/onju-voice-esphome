import esphome.codegen as cg
import esphome.config_validation as cv
from esphome import automation
from esphome.components import text_sensor
from esphome.const import CONF_ID, CONF_TRIGGER_ID

CODEOWNERS = ["@Idskov"]
DEPENDENCIES = []

audio_state_manager_ns = cg.esphome_ns.namespace("audio_state_manager")
AudioStateManager = audio_state_manager_ns.class_("AudioStateManager", cg.Component)

# Trigger classes (one per state, for on_enter_* and on_exit_*)
STATES = [
    "standby", "listening", "processing", "responding",
    "music", "announcing", "alerting",
]

# Generate trigger class references
EnterTriggers = {}
ExitTriggers = {}
for state in STATES:
    enter_name = f"OnEnter{state.capitalize()}Trigger"
    exit_name = f"OnExit{state.capitalize()}Trigger"
    EnterTriggers[state] = audio_state_manager_ns.class_(enter_name, automation.Trigger.template())
    ExitTriggers[state] = audio_state_manager_ns.class_(exit_name, automation.Trigger.template())

# Actions
RequestStateAction = audio_state_manager_ns.class_("RequestStateAction", automation.Action)
PopStateAction = audio_state_manager_ns.class_("PopStateAction", automation.Action)
ForceStandbyAction = audio_state_manager_ns.class_("ForceStandbyAction", automation.Action)

# AudioState enum reference
AudioStateEnum = audio_state_manager_ns.enum("AudioState")

CONF_STATUS_SENSOR = "status_text_sensor"

# Build config schema
schema = {
    cv.GenerateID(): cv.declare_id(AudioStateManager),
    cv.Optional(CONF_STATUS_SENSOR): text_sensor.text_sensor_schema(),
}

# Add on_enter_*/on_exit_* triggers for each state
for state in STATES:
    schema[cv.Optional(f"on_enter_{state}")] = automation.validate_automation(
        {cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(EnterTriggers[state])}
    )
    schema[cv.Optional(f"on_exit_{state}")] = automation.validate_automation(
        {cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(ExitTriggers[state])}
    )

CONFIG_SCHEMA = cv.Schema(schema).extend(cv.COMPONENT_SCHEMA)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)

    # Register text sensor
    if CONF_STATUS_SENSOR in config:
        sens = await text_sensor.new_text_sensor(config[CONF_STATUS_SENSOR])
        cg.add(var.set_status_sensor(sens))

    # Register triggers
    for state in STATES:
        for conf in config.get(f"on_enter_{state}", []):
            trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID], var)
            await automation.build_automation(trigger, [], conf)

        for conf in config.get(f"on_exit_{state}", []):
            trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID], var)
            await automation.build_automation(trigger, [], conf)


# --- Actions (callable from YAML automations) ---

CONF_STATE = "state"

REQUEST_STATE_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.use_id(AudioStateManager),
    cv.Required(CONF_STATE): cv.enum(
        {s.upper(): i for i, s in enumerate(STATES)}, upper=True
    ),
})

POP_STATE_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.use_id(AudioStateManager),
})

FORCE_STANDBY_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.use_id(AudioStateManager),
})


@automation.register_action("audio_state_manager.request_state", RequestStateAction, REQUEST_STATE_SCHEMA, synchronous=True)
async def request_state_action_to_code(config, action_id, template_arg, args):
    parent = await cg.get_variable(config[CONF_ID])
    var = cg.new_Pvariable(action_id, template_arg, parent)
    cg.add(var.set_state(config[CONF_STATE]))
    return var


@automation.register_action("audio_state_manager.pop_state", PopStateAction, POP_STATE_SCHEMA, synchronous=True)
async def pop_state_action_to_code(config, action_id, template_arg, args):
    parent = await cg.get_variable(config[CONF_ID])
    return cg.new_Pvariable(action_id, template_arg, parent)


@automation.register_action("audio_state_manager.force_standby", ForceStandbyAction, FORCE_STANDBY_SCHEMA, synchronous=True)
async def force_standby_action_to_code(config, action_id, template_arg, args):
    parent = await cg.get_variable(config[CONF_ID])
    return cg.new_Pvariable(action_id, template_arg, parent)
