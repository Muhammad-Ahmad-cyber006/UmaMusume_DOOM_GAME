

SOLDIER_STATS = dict(speed=0.024, health=600, attack_damage=90, accuracy=0.08)      # 2 hits
CACO_DEMON_STATS = dict(speed=0.032, health=700, attack_damage=220, accuracy=0.18, attack_dist=1.0)  # 2 hits
CYBER_DEMON_STATS = dict(speed=0.036, health=1200, attack_damage=150, accuracy=0.13, attack_dist=6)  # 3 hits


NPC_AWARENESS_BASE_RADIUS = 12
NPC_AWARENESS_MAX_RADIUS = 50
NPC_AWARENESS_SCALE_START_COUNT = 20
NPC_AWARENESS_FULL_THRESHOLD = 5


def get_npc_awareness_radius(remaining_alive_count):
    if remaining_alive_count <= NPC_AWARENESS_FULL_THRESHOLD:
        return NPC_AWARENESS_MAX_RADIUS
    if remaining_alive_count >= NPC_AWARENESS_SCALE_START_COUNT:
        return NPC_AWARENESS_BASE_RADIUS
    span = NPC_AWARENESS_SCALE_START_COUNT - NPC_AWARENESS_FULL_THRESHOLD
    progress = (NPC_AWARENESS_SCALE_START_COUNT - remaining_alive_count) / span
    return NPC_AWARENESS_BASE_RADIUS + progress * (NPC_AWARENESS_MAX_RADIUS - NPC_AWARENESS_BASE_RADIUS)


NPC_STUCK_FRAMES_THRESHOLD = 8  # frames of near-zero movement before an NPC nudges sideways

GOLDSHIP_STATS = dict(
    speed=0.026, health=5000, attack_damage=380,  
    accuracy=1.0, attack_dist=7,
    attack_cooldown_ms=700,   # real cooldown, independent of animation timing
    size=34,
)
GOLDSHIP_SCALE = 2.6
GOLDSHIP_IDLE_SHIFT = -0.24
GOLDSHIP_ENCOUNTER_SOUND_CHANCE = 0.95  # odds of a bark on first sighting the player

GOLDSHIP_WALK_SHIFT = -0.04
GOLDSHIP_DEATH_SHIFT = -0.05


MINION_STATS = dict(
    speed=0.02, health=600, attack_damage=80,   # 2 hits
    accuracy=1.0,             # the shot itself is dodgeable, no separate miss roll
    attack_dist=10,           # stays back and shoots rather than closing in
    attack_cooldown_ms=1800,
    size=19,
)
MINION_SCALE = 1.4    # reads as a minion

MINION_SHIFT = -0.12
MINION_BOB_AMPLITUDE = 0.05     # fraction of projected height, fakes a walk-bounce
MINION_BOB_PERIOD_MS = 340      # single still image has no walk cycle, so this fakes one
MINION_COUNT_PER_WAVE = 5       # fallback wave size if a caller does not specify one
MINION_CORPSE_LINGER_MS = 1200  # how long the defeat pose stays before removal
MINION_PROJECTILE_SPEED = 0.012
MINION_PROJECTILE_SCALE = 0.10
MINION_PROJECTILE_LIFETIME_MS = 4600
MINION_PROJECTILE_HIT_RADIUS = 0.3


LEVEL1_MINION_WAVES = [
    dict(positions=[(11.5, 5.5), (17.5, 5.5)], tier_multiplier=0.85),
    dict(positions=[(13.5, 11.5), (16.5, 11.5), (14.5, 13.5)], tier_multiplier=1.05),
    dict(positions=[(11.5, 18.5), (19.5, 18.5), (15.5, 20.5), (15.5, 17.5)], tier_multiplier=1.3),
]


MEISHO_DOTO_STATS = dict(speed=0.026, size=45, attack_dist=13, accuracy=1.0)

MEISHO_DOTO_STAGES = [
    dict(health=15000, skin='meisho_doto.png', name='MESHO DOTO',
         scale=2.2, shift=-0.15, speed_multiplier=1.0,
         spawns_minions=False, minion_wave_count=0, minion_tier=1.0, omni_mode=False,
         transform_arrow='MESHO DOTO', transform_banner='MESHO DOTO',
         bar_color=(240, 200, 90)),                                       # stage 1: base form, gold
    dict(health=15000, skin='meisho_doto2.png', name='MESHO DOTO BLACK',
         scale=2.4, shift=-0.10, speed_multiplier=1.25,
         spawns_minions=True, minion_wave_count=5, minion_tier=1.0, omni_mode=False,
         transform_arrow='MESHO DOTO \u2192 BLACK FORM',
         transform_banner='MESHO DOTO HAS ENTERED BLACK FORM',
         bar_color=(150, 150, 165)),                                      # stage 2: steel-black
    dict(health=12000, skin='meisho_doto3.png', name='MESHO DOTO BLACK PURPLE',
         scale=2.6, shift=-0.10, speed_multiplier=1.55,
         spawns_minions=True, minion_wave_count=7, minion_tier=1.2, omni_mode=False,
         transform_arrow='MESHO DOTO \u2192 BLACK PURPLE FORM',
         transform_banner='MESHO DOTO HAS ENTERED BLACK PURPLE FORM',
         bar_color=(180, 80, 235)),                                       # stage 3: black and purple
    dict(health=8000, skin='meisho_doto4.png', name='MESHO DOTO OMNI GOD',
         scale=3.15, shift=-0.15, speed_multiplier=1.7,
         spawns_minions=True, minion_wave_count=6, minion_tier=1.45, omni_mode=True,
         transform_arrow='MESHO DOTO HAS ASCENDED \u2014 OMNI GOD FORM',
         transform_banner='MESHO DOTO HAS ASCENDED \u2014 OMNI GOD FORM',
         bar_color=(255, 70, 90)),                                        # stage 4: final form, red
]
MEISHO_DOTO_TOTAL_HEALTH = sum(stage['health'] for stage in MEISHO_DOTO_STAGES)


MEISHO_DOTO_TRANSFORM_DURATION_MS = 1500

# Stage 1: baseline kit, a readable 5-way fan plus a wider spread volley.
STAGE1_HUGE_ASSET = 'huge_attack.png'
STAGE1_HUGE_COOLDOWN_MS = 4200
STAGE1_HUGE_DAMAGE = 400
STAGE1_HUGE_COUNT = 5
STAGE1_HUGE_SPREAD_DEG = 40
STAGE1_HUGE_SPEED = 0.004
STAGE1_HUGE_SCALE = 0.75
STAGE1_HUGE_HIT_RADIUS = 0.85
STAGE1_HUGE_LIFETIME_MS = 6000

STAGE1_SPREAD_ASSET = 'multi_attack_projectiles.png'
STAGE1_SPREAD_COOLDOWN_MS = 3200
STAGE1_SPREAD_DAMAGE = 110
STAGE1_SPREAD_COUNT = 14
STAGE1_SPREAD_DEG = 70
STAGE1_SPREAD_SPEED = 0.008
STAGE1_SPREAD_SCALE = 0.26
STAGE1_SPREAD_HIT_RADIUS = 0.45
STAGE1_SPREAD_LIFETIME_MS = 3500

# Stage 2: bigger and faster fan plus spread, and a rare 4-way cross burst.
STAGE2_HUGE_ASSET = 'huge_attack_stage2.png'
STAGE2_HUGE_COOLDOWN_MS = 3000
STAGE2_HUGE_DAMAGE = 460
STAGE2_HUGE_COUNT = 7
STAGE2_HUGE_SPREAD_DEG = 55
STAGE2_HUGE_SPEED = 0.0048
STAGE2_HUGE_SCALE = 0.9
STAGE2_HUGE_HIT_RADIUS = 1.0
STAGE2_HUGE_LIFETIME_MS = 6000

STAGE2_SPREAD_ASSET = 'mulit_attack_stage2.png'
STAGE2_SPREAD_COOLDOWN_MS = 2100
STAGE2_SPREAD_DAMAGE = 130
STAGE2_SPREAD_COUNT = 18
STAGE2_SPREAD_DEG = 95
STAGE2_SPREAD_SPEED = 0.0095
STAGE2_SPREAD_SCALE = 0.32
STAGE2_SPREAD_HIT_RADIUS = 0.5
STAGE2_SPREAD_LIFETIME_MS = 3400

STAGE2_CROSS_COOLDOWN_MS = 6800   # long cooldown, stays a rare event
STAGE2_CROSS_ARMS = 4             # north, east, south, west
STAGE2_CROSS_DAMAGE = 340
STAGE2_CROSS_SPEED = 0.0042
STAGE2_CROSS_SCALE = 0.72
STAGE2_CROSS_HIT_RADIUS = 0.8
STAGE2_CROSS_LIFETIME_MS = 5000

# Stage 3: major difficulty spike, bigger and faster still, real 2-part combo.
STAGE3_HUGE_ASSET = 'huge_attack_stage3.png'
STAGE3_HUGE_COOLDOWN_MS = 2300
STAGE3_HUGE_DAMAGE = 520
STAGE3_HUGE_COUNT = 9
STAGE3_HUGE_SPREAD_DEG = 70
STAGE3_HUGE_SPEED = 0.0055
STAGE3_HUGE_SCALE = 1.05
STAGE3_HUGE_HIT_RADIUS = 1.15
STAGE3_HUGE_LIFETIME_MS = 5800

STAGE3_SPREAD_ASSET = 'multi_attack_stage3.png'
STAGE3_SPREAD_COOLDOWN_MS = 1600
STAGE3_SPREAD_DAMAGE = 150
STAGE3_SPREAD_COUNT = 22
STAGE3_SPREAD_DEG = 110
STAGE3_SPREAD_SPEED = 0.0105
STAGE3_SPREAD_SCALE = 0.36
STAGE3_SPREAD_HIT_RADIUS = 0.55
STAGE3_SPREAD_LIFETIME_MS = 3300

STAGE3_CROSS_COOLDOWN_MS = 4200   # more frequent than stage 2
STAGE3_CROSS_ARMS = 6
STAGE3_CROSS_DAMAGE = 380
STAGE3_CROSS_SPEED = 0.0048
STAGE3_CROSS_SCALE = 0.8
STAGE3_CROSS_HIT_RADIUS = 0.88
STAGE3_CROSS_LIFETIME_MS = 5200

STAGE3_COMBO_DELAY_MS = 260       # gap between the fan and its spread follow-up
STAGE3_COMBO_SPREAD_COUNT = 10
STAGE3_COMBO_SPREAD_DEG = 60

# Stage 4: rotating ring plus a periodic aimed burst, counts capped for performance.
OMNI_ASSET = 'omni.png'
OMNI_RING_COOLDOWN_MS = 2800
OMNI_RING_COUNT = 16
OMNI_RING_DAMAGE = 2160
OMNI_RING_SPEED = 0.0035
OMNI_RING_SCALE = 3.6
OMNI_RING_SPAWN_RADIUS = 1.3
OMNI_RING_HIT_RADIUS = 3.4
OMNI_RING_LIFETIME_MS = 7000
OMNI_RING_ROTATION_STEP_DEGREES = 27   # each cast rotates so the gaps do not repeat

OMNI_RING_FIRST_CAST_DELAY_MS = 500

OMNI_BURST_COOLDOWN_MS = 1500
OMNI_BURST_COUNT = 3
OMNI_BURST_SPREAD_DEG = 22
OMNI_BURST_DAMAGE = 700
OMNI_BURST_SPEED = 0.009
OMNI_BURST_SCALE = 0.95
OMNI_BURST_HIT_RADIUS = 0.8
OMNI_BURST_LIFETIME_MS = 4000

OMNI_STAGE_DOT_DAMAGE_PER_SECOND = 150  # continuous chip damage while this stage is active
