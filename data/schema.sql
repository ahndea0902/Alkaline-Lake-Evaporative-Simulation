-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Table: water_system (Water sytstem information)
CREATE TABLE water_system (
  ws_id   INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique ID for each water system
  ws_name TEXT    NULL                       -- Water system name
);

-- Table: water_body (Water body information)
CREATE TABLE water_body (
  wb_id   INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique ID for each water body
  ws_id   INTEGER NOT NULL,                  -- Reference to water_system
  wb_type TEXT    NULL,                      -- Water body type (river, lake, well, etc.)
  wb_name TEXT    NULL,                      -- Name of the water body
  wb_abbr TEXT    NULL,                      -- Water body abbreviation
  FOREIGN KEY(ws_id)
    REFERENCES water_system(ws_id)           -- Foreign key constraint
);

-- Table: sample (Sample metadata)
CREATE TABLE sample (
  smp_id      INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique ID for each sample
  wb_id       INTEGER NOT NULL,                  -- Reference to sample_point
  smp_station TEXT    NULL,                      -- Sampling Station
  smp_date    TEXT    NULL,                      -- Sampling timestamp (ISO8601)
  smp_name    TEXT    NULL,                      -- Sample name (e.g., SLG01)
  smp_type    TEXT    NULL,                      -- Sample type (water, solid)
  lat         REAL    NULL,                      -- Latitude coordinate
  lng         REAL    NULL,                      -- Longitude coordinate
  elev        REAL    NULL,                      -- Elevation coordinate
  memo        TEXT    NULL,                      -- Sample memo
  FOREIGN KEY(wb_id)
    REFERENCES water_body(wb_id)                 -- Foreign key constraint
);

-- Table: measurement (Measured water quality parameters)
CREATE TABLE measurement (
  meas_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique ID for each measurement
  smp_id  INTEGER NOT NULL,                  -- Reference to sample
  param   TEXT    NOT NULL,                  -- Measured parameter name (pH, alkalinity, discharge, etc.)
  value   REAL    NULL,                      -- Measured value
  unit    TEXT    NULL,                      -- Unit of measurement
  FOREIGN KEY(smp_id)
    REFERENCES sample(smp_id)                -- Foreign key constraint
);

-- Table: instrumental_measurement (Instrumentally analized water quality values)
CREATE TABLE instrumental_measurement (
  inst_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique ID for each computed record
  smp_id  INTEGER NOT NULL,                  -- Reference to sample
  ion_sp  TEXT    NOT NULL,                  -- Ion species (Ca++, Cl-, etc.)
  conc    REAL    NULL,                      -- Analyzed concentration
  unit    TEXT    NOT NULL,                  -- Unit of concentration
  FOREIGN KEY(smp_id)
    REFERENCES sample(smp_id)                -- Foreign key constraint
);

-- Table: phreeqc_calculation (Water quality calculation)
CREATE TABLE phreeqc_calculation (
  phrq_id   INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique ID for each phreeqc calculation
  smp_id    INTEGER NOT NULL,                  -- Reference to sample
  param     TEXT    NOT NULL,                  -- phreeqc calculation parameter
  value     REAL    NULL,                      -- Analyzed parameter
  unit      TEXT    NOT NULL,                  -- Unit of parameter
  FOREIGN KEY(smp_id)
    REFERENCES sample(smp_id)                  -- Foreign key constraint
);

-- Table: evaporative_simulation (Simulation metadata)
CREATE TABLE evaporative_simulation (
  evap_id   INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique ID for each evaporative simulation run
  smp_id    INTEGER NOT NULL,                  -- Reference to sample
  evap_name TEXT    NOT NULL,                  -- Name of the evaporative simulation run
  evap_date TEXT    NOT NULL,                  -- Simulation timestamp (ISO8601)
  param     TEXT    NOT NULL,                  -- JSON string of parameters
  FOREIGN KEY(smp_id)
    REFERENCES sample(smp_id)                  -- Foreign key constraint
);

-- Table: evaporative_simulation_cell (Simulation grid cell values)
CREATE TABLE evaporative_simulation_cell (
  cell_id    INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique ID for each cell
  evap_id    INTEGER NOT NULL,                  -- Reference to simulation_run
  row_idx    INTEGER NOT NULL,                  -- Row index in grid
  col_idx    INTEGER NOT NULL,                  -- Column index in grid
  header     TEXT    NOT NULL,                  -- Header
  value      REAL    NULL,                      -- Cell value
  FOREIGN KEY(evap_id)
    REFERENCES evaporative_simulation(evap_id)  -- Foreign key constraint
);