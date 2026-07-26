// Operator constants for notam.html.
//
// Loaded as a classic <script> because notam.html runs from file://, where
// Chrome blocks fetch() and ES modules. Edit this file directly to add sites,
// aircraft or aerodromes; the tool also lets you add them at runtime and keeps
// those in localStorage.
//
// "verified" means the value has been checked against a primary source. Entries
// with verified:false are starting points only -- the tool badges them in the UI
// so an unchecked figure can never quietly end up on a submission.

var NOTAM_PROFILES = {

  // Fixed for every NOTAM this group raises.
  group: 'UA_AERIALROBOTICSAUS',
  fir: 'YMMM',

  // Aerodrome reference points, with the variation PUBLISHED IN ERSA -- not the
  // WMM value. Charted MAG bearings are against published variation, and the
  // published figure is what reproduces the bearings on the known-good references.
  aerodromes: [
    {
      id: 'YSCB',
      name: 'CANBERRA AD',
      // ERSA ARP S35 18.4 E149 11.7.
      lat: -(35 + 18.4 / 60),
      lon: 149 + 11.7 / 60,
      variation: 12.0, // degrees EAST
      verified: true,
      note: 'Reproduces BRG 209 on C3031/25, BRG 227 on C2048/26 and BRG 263 on template 1278.'
    },
    { id: 'YSSY', name: 'SYDNEY AD',       lat: -(33 + 56.7 / 60), lon: 151 + 10.7 / 60, variation: 12.7, verified: false },
    { id: 'YMML', name: 'MELBOURNE AD',    lat: -(37 + 40.4 / 60), lon: 144 + 50.6 / 60, variation: 11.5, verified: false },
    { id: 'YSBK', name: 'BANKSTOWN AD',    lat: -(33 + 55.4 / 60), lon: 150 + 59.3 / 60, variation: 12.6, verified: false },
    { id: 'YSCN', name: 'CAMDEN AD',       lat: -(34 +  2.4 / 60), lon: 150 + 41.3 / 60, variation: 12.5, verified: false },
    { id: 'YSNW', name: 'NOWRA AD',        lat: -(34 + 56.9 / 60), lon: 150 + 32.2 / 60, variation: 12.6, verified: false },
    { id: 'YCOM', name: 'COOMA AD',        lat: -(36 + 18.0 / 60), lon: 148 + 58.4 / 60, variation: 12.2, verified: false },
    { id: 'YWLM', name: 'WILLIAMTOWN AD',  lat: -(32 + 47.7 / 60), lon: 151 + 50.2 / 60, variation: 12.4, verified: false }
  ],

  // Item E) Subject descriptor. C-MAN0284 v7 s12.2 requires the type and the
  // weight, and requires the words "UA" rather than RPA / RPAS / UAV / drone.
  aircraft: [
    { label: 'Multi-rotor 6kg',      descriptor: 'MULTI-ROTOR 6KG',  verified: true,  note: 'As used on C3031/25.' },
    { label: 'Powered lift 9kg',     descriptor: 'POWERED LIFT 9KG', verified: true,  note: 'As used on stored template 1278.' },
    { label: 'Powered lift 12kg',    descriptor: 'POWERED LIFT 12KG', verified: true, note: 'As used on C2048/26.' },
    { label: 'Carbonix Ottano',      descriptor: 'POWERED LIFT 60KG', verified: false, note: 'MTOW from the ReOC variation RPAS2023-07841; confirm the descriptor wording.' },
    { label: 'Carbonix Volanti',     descriptor: 'POWERED LIFT ??KG', verified: false },
    { label: 'ARACE Griffin Pro',    descriptor: 'POWERED LIFT ??KG', verified: false },
    { label: 'ARACE Angel',          descriptor: 'POWERED LIFT ??KG', verified: false }
  ],

  contacts: [
    { name: 'ANDREW TRIDGELL', phone: '0412 666 929', verified: true, note: 'From the NIS NOTAM group registration form.' },
    { name: '',                phone: '0408 479 339', verified: false, note: 'Appears on stored template 1278; name unknown.' }
  ],

  // Broadcast frequency quoted in the Item E) text.
  frequencies: [
    { label: '125.9 (Melbourne Centre, Canberra area)', value: '125.9', verified: true },
    { label: '126.7 (CTAF)',                            value: '126.7', verified: false }
  ],

  // Item E) text is assembled from these lines. {{...}} placeholders are
  // substituted; a line whose placeholders are all empty is dropped.
  textLines: [
    'OPR WI {{RADIUS}} OF PSN {{POSITION}} BRG {{BEARING}} MAG {{DISTANCE}} FM {{AD_NAME}} ({{AD_ID}})',
    'ALL OPS WILL BE OUTSIDE CONTROLLED AIRSPACE',
    'OPR WILL BCST ON FREQ {{FREQ}} WITHIN 15MIN PRIOR LAUNCH',
    'OPR CTC TEL: {{PHONE}}'
  ],

  // Saved operations. Load one, change the dates, done.
  sites: [
    {
      label: 'C3031/25 (18 Dec 2025) -- reference case',
      lat: -(35 + 34 / 60 + 40 / 3600),
      lon: 148 + 54 / 60 + 29 / 3600,
      radiusNm: 1.0,
      ceilingFt: 5500,
      aerodrome: 'YSCB',
      aircraft: 'Multi-rotor 6kg',
      contact: 'ANDREW TRIDGELL',
      freq: '125.9'
    },
    {
      label: 'C2048/26 (27 Jul 2026) -- reference case',
      lat: -(35 + 26 / 60 + 24 / 3600),
      lon: 148 + 55 / 60 + 26 / 3600,
      radiusNm: 10.7,
      ceilingFt: 5800,
      aerodrome: 'YSCB',
      aircraft: 'Powered lift 12kg',
      contact: 'ANDREW TRIDGELL',
      freq: '125.9'
    },
    {
      label: 'Template 1278 -- Spring Valley 7NM',
      lat: -(35 + 17 / 60 + 15 / 3600),
      lon: 148 + 55 / 60 + 11 / 3600,
      radiusNm: 7.0,
      ceilingFt: 4900,
      aerodrome: 'YSCB',
      aircraft: 'Powered lift 9kg',
      contact: '',
      freq: '125.9'
    }
  ],

  defaults: {
    timezone: 'Australia/Sydney',
    bufferNm: 0.5,   // added to the mission's enclosing circle
    status: 'WILL TAKE PLACE'
  }
};
