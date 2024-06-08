--
-- Table structure for table competitions
--

CREATE TABLE competitions (
  id int(11) PRIMARY KEY,
  `name` varchar(255) NOT NULL,
  auto_upload_results tinyint(1) NOT NULL DEFAULT 1,
  show_score tinyint(1) NOT NULL DEFAULT 1,
  show_teams tinyint(1) NOT NULL DEFAULT 1
);

--
-- Dumping data for table competitions
--

INSERT INTO competitions VALUES
  (3, 'F-League', 0, 1, 1),
  (8, 'Ipswich Futsal Premier League', 1, 1, 1);

----------------------------------------------------------

--
-- Table structure for table competition_period_configurations
--

CREATE TABLE competition_period_configurations (
  competition_id int(11),
  period_config_id int(11) NOT NULL,
  PRIMARY KEY (competition_id, period_config_id)
);

--
-- Dumping data for table competition_period_configurations
--

INSERT INTO competition_period_configurations VALUES
  (3, 4),
  (8, 1),
  (8, 2);

-- --------------------------------------------------------

--
-- Table structure for table competition_teams
--

CREATE TABLE competition_teams (
  season_id varchar(12) NOT NULL,
  competition_id int(11) NOT NULL,
  team_id int(11) NOT NULL,
  PRIMARY KEY (season_id, competition_id, team_id)
);

--
-- Dumping data for table competition_teams
--

INSERT INTO competition_teams VALUES
  ('2022 - 2023', 3, 18),
  ('2022 - 2023', 3, 20),
  ('2022 - 2023', 3, 21),
  ('2022 - 2023', 3, 23),
  ('2022 - 2023', 3, 112),
  ('2022 - 2023', 3, 113),
  ('2022 - 2023', 3, 114),
  ('2022 - 2023', 3, 115),
  ('2022 - 2023', 3, 116),
  ('2022 - 2023', 8, 106),
  ('2022 - 2023', 8, 107),
  ('2022 - 2023', 8, 108),
  ('2022 - 2023', 8, 109),
  ('2022 - 2023', 8, 110),
  ('2022 - 2023', 8, 111),
  ('2022 - 2023', 8, 117);

-- --------------------------------------------------------

--
-- Table structure for table fixtures
--

CREATE TABLE fixtures (
  id int(11) PRIMARY KEY,
  season varchar(12) NOT NULL,
  competition int(11) NOT NULL,
  round_type varchar(8) NOT NULL,
  round_number int(3) NOT NULL,
  home_team int(11) NOT NULL,
  home_score int(2) NOT NULL DEFAULT 0,
  away_score int(2) NOT NULL DEFAULT 0,
  away_team int(11) NOT NULL,
  match_date date NOT NULL,
  match_datetime datetime NOT NULL,
  venue varchar(100) NOT NULL,
  home_penalties int(2) NOT NULL DEFAULT 0,
  away_penalties int(2) NOT NULL DEFAULT 0
);

--
-- Dumping data for table fixtures
--

INSERT INTO fixtures VALUES
  (3151011, '2022 - 2023', 3, 'Regular', 1, 113, 0, 0, 116, '2023-06-14', '2023-06-14 16:30:00', 'Ripley Valley SSC - Court B', 0, 0),
  (8200219, '2022 - 2023', 8, 'Finals', 3, 110, 0, 0, 117, '2023-06-14', '2023-06-14 15:30:00', 'Ripley Valley SSC - Court B', 0, 0);

-- --------------------------------------------------------

--
-- Table structure for table periods
--

CREATE TABLE periods (
  id int(11) PRIMARY KEY,
  `name` varchar(200) NOT NULL,
  display_name varchar(100) NOT NULL,
  `length` int(11) DEFAULT NULL,
  derscription varchar(1000) NOT NULL,
  auto_start tinyint(1) NOT NULL DEFAULT 1,
  can_pause tinyint(1) NOT NULL DEFAULT 1,
  count_up tinyint(1) NOT NULL DEFAULT 0,
  end_siren tinyint(1) NOT NULL DEFAULT 1,
  last_minute_decimal tinyint(1) NOT NULL DEFAULT 0,
  reset_fouls tinyint(1) NOT NULL DEFAULT 0,
  show_time tinyint(1) NOT NULL DEFAULT 1,
  show_time_zero tinyint(1) NOT NULL DEFAULT 0,
  show_time_ticker tinyint(1) NOT NULL DEFAULT 1,
  decides_extra_time tinyint(1) NOT NULL DEFAULT 0,
  decides_penalties tinyint(1) NOT NULL DEFAULT 0
);

--
-- Dumping data for table periods
--

INSERT INTO periods VALUES
  (1, 'Pre game IF', 'Pre game', NULL, 'Pre game period for Ipswich Futsal social fixtures.', 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0),
  (2, 'First half IF', 'First half', 1080000, 'Standard 18 minute first half for Ipswich Futsal social fixtures.', 0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0),
  (3, 'Half time IF', 'Half time', 120000, 'Standard 2 minute half time period for Ipswich Futsal social fixtures.', 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0),
  (4, 'Second half IF', 'Second half', 1080000, 'Standard 18 minute second half for Ipswich Futsal social fixtures.', 0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0),
  (5, 'Full time IF', 'Full time', 30000, 'Standard 20 second full time display for Ipswich Futsal social fixtures.', 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0),
  (6, 'Late updates IF', 'Late updates', 30000, 'End of second half period for late updates (e.g. free kick taken after end of second half) in Ipswich Futsal social finals fixtures.', 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0),
  (7, 'Normal FT IF', 'Normal FT', 90000, 'Normal full time period before extra time (if needed) in Ipswich Futsal social finals fixture.', 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0),
  (8, 'First half ET IF', 'First half ET', 300000, 'First half of extra time for Ipswich Futsal social finals fixture', 0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0),
  (9, 'Half time ET IF', 'Half time ET', 60000, 'Half time during extra time of Ipswich Futsal social finals fixture', 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0),
  (10, 'Second half ET IF', 'Second half ET', 300000, 'Second half of extra time for Ipswich Futsal social finals fixture', 0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0),
  (11, 'Full time ET IF', 'Full time ET', 30000, 'Period at full time of extra time which gives opportunities for late adjustments to the score. If the score is level, go to penalties. If not, go to full time.', 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1),
  (12, 'Penalties IF', 'Penalties', 2000, 'Period for penalty shootout after extra time.', 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0),
  (13, 'Pre game F-League', 'Pre game', NULL, 'Pre game period for an F-League fixture.', 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0),
  (14, 'First half F-League', 'First half', 1200000, 'First half period for F-League', 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0),
  (15, 'Half time F-League', 'Half time', 480000, 'Half time period for F-League', 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0),
  (16, 'Second half F-League', 'Second half', 1200000, 'Second half period for F-League', 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0),
  (17, 'Full time F-League', 'Full time', 300000, 'Full time period for F-League', 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0);

-- --------------------------------------------------------

--
-- Table structure for table period_configurations
--

CREATE TABLE period_configurations (
  id int(11) PRIMARY KEY,
  name varchar(100) NOT NULL,
  round_type varchar(50) NOT NULL,
  minimum_pregame int(11) NOT NULL DEFAULT 90000,
  description varchar(1000) NOT NULL
);

--
-- Dumping data for table period_configurations
--

INSERT INTO period_configurations VALUES
  (1, 'Ipswich Futsal Regular', 'Regular', 90000, 'Period configuration for regular Ipswich Futsal social fixtures.'),
  (2, 'Ipswich Futsal Finals', 'Finals', 90000, 'Period configuration for Ipswich Futsal social finals fixtures.'),
  (4, 'F-League Regular', 'Regular', 90000, 'Period configuration for a regular F-League fixture');

-- --------------------------------------------------------

--
-- Table structure for table period_config_periods
--

CREATE TABLE period_config_periods (
  configuration_id int(11) NOT NULL,
  period_id int(11) NOT NULL,
  sort_order int(11) NOT NULL,
  PRIMARY KEY (configuration_id, period_id)
);

--
-- Dumping data for table period_config_periods
--

INSERT INTO period_config_periods VALUES
  (1, 1, 0),
  (1, 2, 1),
  (1, 3, 2),
  (1, 4, 3),
  (1, 5, 4),
  (2, 1, 0),
  (2, 2, 1),
  (2, 3, 2),
  (2, 4, 3),
  (2, 5, 10),
  (2, 6, 4),
  (2, 7, 5),
  (2, 8, 6),
  (2, 10, 7),
  (2, 11, 8),
  (2, 12, 9),
  (4, 13, 0),
  (4, 14, 1),
  (4, 15, 2),
  (4, 16, 3),
  (4, 17, 4);

-- --------------------------------------------------------

--
-- Table structure for table seasons
--

CREATE TABLE seasons (
  id varchar(12) PRIMARY KEY,
  `name` varchar(50) NOT NULL,
  `start_date` date NOT NULL,
  end_date date NOT NULL
);

--
-- Dumping data for table seasons
--

INSERT INTO seasons VALUES
  ('2022 - 2023', 'Summer 2022-2023', '2022-10-01', '2023-03-11');

-- --------------------------------------------------------

--
-- Table structure for table season_competitions
--

CREATE TABLE season_competitions (
  season_id varchar(12) NOT NULL,
  competition_id int(11) NOT NULL,
  PRIMARY KEY (season_id, competition_id)
);

--
-- Dumping data for table season_competitions
--

INSERT INTO season_competitions VALUES
  ('2022 - 2023', 3),
  ('2022 - 2023', 8);


-- --------------------------------------------------------

--
-- Table structure for table teams
--

CREATE TABLE teams (
  id int(11) PRIMARY KEY,
  `name` varchar(200) NOT NULL,
  colour varchar(50) NOT NULL,
  abbreviation varchar(5) NOT NULL,
  logo varchar(100) DEFAULT NULL
);

--
-- Dumping data for table teams
--

INSERT INTO teams VALUES
  (18, 'Ipswich Futsal', '#00591E', 'IPS', NULL),
  (21, 'Galaxy FC', '#E6730F', 'GAL', 'galaxy-fc-logo'),
  (22, 'Gold Coast Force', 'navy', 'GCF', 'force-logo'),
  (23, 'River City FC', '#600000', 'RIV', 'river-city-logo'),
  (106, 'Skillz Cartel FC', '#7030A0', 'SKI', 'skillz-cartel-fc'),
  (107, 'Ring Ins FC', '#FF0000', 'RIFC', 'ring-ins-fc'),
  (108, 'Barcenal FC', 'orange', 'BAR', 'barcenal-fc'),
  (109, 'Dad Bod FC', 'white', 'DAD', 'dad-bod-fc'),
  (110, 'Brisol FC', '#02A852', 'BRI', 'brisol-fc'),
  (111, 'Dixie Normus FC', '#009639', 'DIX', 'dixie-normus-fc'),
  (112, 'Sunshine Coast Wave', '#4BC7ED', 'SCW', 'sunshine-coast-wave'),
  (113, 'Sala Time', 'purple', 'SAL', 'sala-time'),
  (114, 'Arana United FC', 'maroon', 'ARA', 'arana-united-fc'),
  (115, 'Brisbane Elitefoot FC', 'gold', 'ELF', 'elitefoot-fc'),
  (116, 'South Brisbane', 'red', 'SBR', 'south-brisbane'),
  (117, 'Beercelona FC', '#FFA10A', 'BEE', 'beercelona-fc');

-- --------------------------------------------------------

--
-- Table structure for table venues
--

CREATE TABLE venues (
  id int(11) PRIMARY KEY,
  `name` varchar(100) NOT NULL,
  court varchar(1) NOT NULL
);

--
-- Dumping data for table venues
--

INSERT INTO venues VALUES
  (1, 'Ripley Valley SSC - Court A', 'A'),
  (2, 'Ripley Valley SSC - Court B', 'B');

-- --------------------------------------------------------

--
-- Table structure for table players
--

CREATE TABLE players(
  id int(11) PRIMARY KEY
  first_name varchar(100) NOT NULL,
  last_name varchar(100) NOT NULL,
  middle_names varchar(100)
);

--
-- Dumping data for table players
--

INSERT INTO players VALUES
  (1, 'Lachie', 'Blaine');



CREATE TABLE team_players(
  season varchar(12),
  team_id int(11),
  player_id int(11),
  default_shirt_number int(3)
  PRIMARY KEY (season, team_id, player_id)
);

INSERT INTO team_players VALUES
  ('2022-2023', 108, 1, 4);



CREATE TABLE player_appearances(
  player_id int(11),
  team_id int(11),
  fixture_id int(11),
  season varchar(12),
  starting_team boolean,
  subbed_on_time int(11),
  subbed_off_time int(11),
  PRIMARY KEY (player_id, fixture_id)
)



CREATE TABLE events(
  id int(11) PRIMARY KEY,
  name varchar(50)
)



CREATE TABLE player_events(
  player_id int(11),
  team_id int(11),
  fixture_id int(11),
  event_id int(11),
  season varchar(12),
  event_time int(11),
  PRIMARY KEY (player_id, fixture_id,  )
)