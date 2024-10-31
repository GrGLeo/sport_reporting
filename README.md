#     ______          __      ____                
#    / ________  ____/ __  __/ __ \____ _________ 
#   / __/ / __ \/ __  / / / / /_/ / __ `/ ___/ _ \
#  / /___/ / / / /_/ / /_/ / _, _/ /_/ / /__/  __/
# /_____/_/ /_/\__,_/\__,_/_/ |_|\__,_/\___/\___/ 
#                                                 
# 

# Workout Analytics Platform

This platform is designed to analyze swim, bike, and run workouts using key metrics such as Training Stress Score (TSS), Chronic Training Load (CTL), Acute Training Load (ATL), and Training Stress Balance (TSB).

## Calendar view

This allow the user to see all activities done, and by clicking on an acitivity, the user can see in details the workout, planned workout are also available, and on click show the program.

## Analytics
In this, the user can see the detail, of the workout, the metrics per lap, the time spent in the five zones. Two graph are available, one showes the pace and heart rate, the second one shows the average pace per lap.

## Workout planner
In this section, the user can create a workout, through a form two step are mandatory, warm up and cooldown, then set can be added, with one active and one rest period. The workout is then uploaded and shown on the calendar, and be download and used on a Garmin watch, the upload need to be done by connecting the watch to a computer.

## View plan
After selecting in the calendar, a planned workout, this page simply show the workout, pace or power per lap.

## Upload
A .fit file can be upload, and this will show up in the calendar, and Home page metrics will be updated

## Threshold Update
This allow, the user to set his threshold, zones will be calculated, for futur uses. And threshold can be updated to have metrics calculated with up to date metrics.


# Roadmap
Here’s the current roadmap for the project.

- [ ] **Q4 2024** - Initial Release
  - [ ] Fixing planned workout, for cycling and more than one set 
  - [ ] Adding feedback and activity for RPE 
  - [ ] Complete CI/CD

- [ ] **Q1 2025** - Generating Workout 
  - [ ] Generate a workout based on past activities 
  - [ ] Build LoadBalancer 
  - [ ] Adding intra workout calories consumption tracking 
  - [ ] Overall improvement in UX

# Key Metrics

### Training Stress Score (TSS)

**TSS** quantifies the training load of a workout based on its intensity and duration.

**Formula**:

```math
\text{TSS} = \frac{\text{Duration} \times \text{IF}^2 \times 100}{\text{FTP}}
```


- **Duration**: The time spent on the workout in minutes.
- **IF (Intensity Factor)**: The ratio of the normalized power (or pace) to the athlete’s functional threshold power (FTP) or pace.
- **FTP (Functional Threshold Power)**: The highest power output (or pace) that an athlete can maintain in a quasi-steady state for approximately 1 hour.

### Chronic Training Load (CTL)

**CTL** represents the long-term training load, often referred to as "fitness." It is calculated as the exponentially weighted moving average (EWMA) of TSS over a 42-day period.

**Formula**:

```math
\text{CTL}_\text{today} = \text{CTL}_\text{yesterday} + \frac{\text{TSS}_\text{today} - \text{CTL}_\text{yesterday}}{42}
```


### Acute Training Load (ATL)

**ATL** represents the short-term training load, often referred to as "fatigue." It is calculated as the exponentially weighted moving average of TSS over a 7-day period.

**Formula**:

```math
\text{ATL}_\text{today} = \text{ATL}_\text{yesterday} + \frac{\text{TSS}_\text{today} - \text{ATL}_\text{yesterday}}{7}
```

### Training Stress Balance (TSB)

**TSB** is the difference between CTL and ATL, often referred to as "form." It indicates an athlete's readiness to perform.

**Formula**:

```math
\text{TSB} = \text{CTL} - \text{ATL}
```

