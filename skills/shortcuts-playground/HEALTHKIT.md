# HealthKit Shortcuts Reference

Health actions are iOS/iPadOS-first. macOS Shortcuts syncs their XML but cannot fully configure the Health UI. Prefer this file and the local reference data over guesses.

## Evidence

Primary syntax source: Federico's local iPhone XML exports in iCloud Drive `* Temp Files`.

- `HealthSnap.xml`: Find Health Samples, `WFHealthQuantityType`, `WFContentItemFilter`, sample output wiring.
- Initial `Log Health Sample.xml` observation: Caffeine quantity log. The scratch export file was later overwritten while testing category values.
- `Log Health Sample - Bloating.xml`: category sample with no visible Value row in the editor.
- `Log Health Sample - Cervical Mucus Quality.xml`: category sample with an explicit enum value picker.
- `Get Details of Health Sample.xml`: Get Details of Health Sample, `WFContentItemPropertyName`, `WFInput`.
- `Log Workout.xml`: action identifier sync/export evidence only; the local export was UUID-only before a full workout configuration was captured.

Exhaustive value source: local Xcode iPhoneOS 26.2 HealthKit headers plus local ActionKit `WFHealthKitConstants.plist`, generated into `data/healthkit-ios26.2-reference.json`.

## Actions

### Find Health Samples

Identifier: `is.workflow.actions.filter.health.quantity`

Required parameters:

- `UUID`
- `WFHealthQuantityType`: Shortcuts UI label, for example `Caffeine`, `Step Count`, `Walking + Running Distance`.
- `WFContentItemFilter`: `WFContentPredicateTableTemplate`.

Optional:

- `WFContentItemLimitEnabled`: boolean.
- `WFContentItemLimitNumber`: required when limit is enabled.

Observed filter from `HealthSnap.xml`:

```xml
<key>WFHealthQuantityType</key>
<string>Caffeine</string>
<key>WFContentItemFilter</key>
<dict>
    <key>Value</key>
    <dict>
        <key>WFActionParameterFilterPrefix</key>
        <integer>1</integer>
        <key>WFContentPredicateBoundedDate</key>
        <false/>
        <key>WFActionParameterFilterTemplates</key>
        <array>
            <dict>
                <key>Operator</key>
                <integer>1002</integer>
                <key>Property</key>
                <string>Start Date</string>
                <key>Removable</key>
                <true/>
                <key>Values</key>
                <dict/>
            </dict>
        </array>
    </dict>
    <key>WFSerializationType</key>
    <string>WFContentPredicateTableTemplate</string>
</dict>
```

Output name observed in downstream wiring: `Health Samples`.

### Get Details of Health Sample

Identifier: `is.workflow.actions.properties.health.quantity`

Required parameters:

- `UUID`
- `WFContentItemPropertyName`
- `WFInput`

Detail names exposed by the iOS picker:

`Type`, `Value`, `Unit`, `Start Date`, `End Date`, `Duration`, `Source`, `Name`.

Observed wiring:

```xml
<key>WFContentItemPropertyName</key>
<string>Value</string>
<key>WFInput</key>
<dict>
    <key>Value</key>
    <dict>
        <key>OutputName</key>
        <string>Health Samples</string>
        <key>OutputUUID</key>
        <string>FIND-HEALTH-SAMPLES-UUID-HERE</string>
        <key>Type</key>
        <string>ActionOutput</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFTextTokenAttachment</string>
</dict>
```

`WFInput` must reference Find Health Samples or a variable sourced from Find Health Samples. Log Health Sample output is also a Health sample source.

### Log Health Sample

Identifier: `is.workflow.actions.health.quantity.log`

Required parameters:

- `UUID`
- `WFQuantitySampleType`
- A value field: usually `WFQuantitySampleQuantity`; enum category samples can also include `WFCategorySampleEnumeration`.

Quantity sample, Caffeine. This shape was observed in the initial scratch export before later category testing overwrote `Log Health Sample.xml`:

```xml
<key>WFQuantitySampleType</key>
<string>Caffeine</string>
<key>WFQuantitySampleQuantity</key>
<dict>
    <key>Value</key>
    <dict>
        <key>Magnitude</key>
        <string>120</string>
        <key>Unit</key>
        <string>mg</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFQuantityFieldValue</string>
</dict>
<key>WFQuantitySampleAdditionalQuantity</key>
<dict>
    <key>Value</key>
    <dict>
        <key>Unit</key>
        <string>mg</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFQuantityFieldValue</string>
</dict>
```

Category sample with no visible value row, Bloating:

```xml
<key>WFQuantitySampleType</key>
<string>Bloating</string>
<key>WFQuantitySampleQuantity</key>
<dict>
    <key>Value</key>
    <dict>
        <key>Magnitude</key>
        <string>10</string>
        <key>Unit</key>
        <string>count</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFQuantityFieldValue</string>
</dict>
<key>WFQuantitySampleAdditionalQuantity</key>
<dict>
    <key>Value</key>
    <dict>
        <key>Unit</key>
        <string>count</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFQuantityFieldValue</string>
</dict>
```

Category sample with enum value, Cervical Mucus Quality:

```xml
<key>WFQuantitySampleType</key>
<string>Cervical Mucus Quality</string>
<key>WFCategorySampleEnumeration</key>
<string>Dry</string>
<key>WFQuantitySampleQuantity</key>
<dict>
    <key>Value</key>
    <dict>
        <key>Magnitude</key>
        <string>10</string>
        <key>Unit</key>
        <string>count</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFQuantityFieldValue</string>
</dict>
<key>WFQuantitySampleAdditionalQuantity</key>
<dict>
    <key>Value</key>
    <dict>
        <key>Unit</key>
        <string>count</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFQuantityFieldValue</string>
</dict>
```

Optional date fields:

- `WFQuantitySampleDate`
- `WFSampleEndDate`

These can use `WFTextTokenAttachment` with `{Type: CurrentDate}`.

### Log Workout

Identifier: `is.workflow.actions.health.workout.log`

The local XML export currently proves the identifier but not a fully configured parameter dictionary. The generator and validator support the schema below from local action metadata conventions and HealthKit workout values; treat a future full iPhone export as higher priority if it conflicts.

Required:

- `UUID`
- `WFWorkoutReadableActivityType`: Shortcuts UI label, for example `Running`, `Walking`, `Cycling`.

Optional:

- `WFWorkoutDate`
- `WFWorkoutDuration`: `WFQuantityFieldValue`, normally `min`.
- `WFWorkoutCaloriesQuantity`: `WFQuantityFieldValue`, normally `kcal`.
- `WFWorkoutDistanceQuantity`: `WFQuantityFieldValue`, normally `m`, `km`, `mi`, etc.

Generated shape:

```xml
<key>WFWorkoutReadableActivityType</key>
<string>Running</string>
<key>WFWorkoutDate</key>
<dict>
    <key>Value</key>
    <dict>
        <key>Type</key>
        <string>CurrentDate</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFTextTokenAttachment</string>
</dict>
<key>WFWorkoutDuration</key>
<dict>
    <key>Value</key>
    <dict>
        <key>Magnitude</key>
        <string>30</string>
        <key>Unit</key>
        <string>min</string>
    </dict>
    <key>WFSerializationType</key>
    <string>WFQuantityFieldValue</string>
</dict>
```

## Values

`data/healthkit-ios26.2-reference.json` contains:

- 120 quantity types.
- 70 category types.
- 17 category value enum families, covering 61 explicit enum values.
- 84 workout activity types.
- 46 ActionKit Health unit strings.

Use `shortcut_label_guess` as a good default, but prefer `observed_shortcuts_labels` when present. Some labels differ by action context: `HKQuantityTypeIdentifierActiveEnergyBurned` has been observed as both `Active Energy Burned` and `Active Energy`.

Known local label override:

- `HKCategoryTypeIdentifierGeneralizedBodyAche`: Shortcuts picker label is `Body and Muscle Ache`, not the SDK-derived `Generalized Body Ache`.

The validator checks Health sample types, Find Health Samples quantity types, workout activity types, category enum values, and units against this local reference when it is available.

## Safety

Do not run Health-writing shortcuts only to test syntax. Build, inspect, validate, export, and import them; leave actual Health writes to the user unless they explicitly ask to run the shortcut.
