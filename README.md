# Workout Analytics Platform

This platform is designed to analyze swim, bike, and run workouts using key metrics such as Training Stress Score (TSS), Chronic Training Load (CTL), Acute Training Load (ATL), and Training Stress Balance (TSB).

## Key Metrics

### Training Stress Score (TSS)

**TSS** quantifies the training load of a workout based on its intensity and duration.

**Formula**:

$\text{TSS} = \frac{\text{Duration} \times \text{IF}^2 \times 100}{\text{FTP}}$


- **Duration**: The time spent on the workout in minutes.
- **IF (Intensity Factor)**: The ratio of the normalized power (or pace) to the athlete’s functional threshold power (FTP) or pace.
- **FTP (Functional Threshold Power)**: The highest power output (or pace) that an athlete can maintain in a quasi-steady state for approximately 1 hour.

### Chronic Training Load (CTL)

**CTL** represents the long-term training load, often referred to as "fitness." It is calculated as the exponentially weighted moving average (EWMA) of TSS over a 42-day period.

**Formula**:

$$
\text{CTL}_\text{today} = \text{CTL}_\text{yesterday} + \frac{\text{TSS}_\text{today} - \text{CTL}_\text{yesterday}}{42}
$$


### Acute Training Load (ATL)

**ATL** represents the short-term training load, often referred to as "fatigue." It is calculated as the exponentially weighted moving average of TSS over a 7-day period.

**Formula**:

$\text{ATL}_\text{today} = \text{ATL}_\text{yesterday} + \frac{\text{TSS}_\text{today} - \text{ATL}_\text{yesterday}}{7}$


### Training Stress Balance (TSB)

**TSB** is the difference between CTL and ATL, often referred to as "form." It indicates an athlete's readiness to perform.

**Formula**:

$\text{TSB} = \text{CTL} - \text{ATL}$

