mod generated;

use std::collections::HashMap;
use std::sync::{Arc, LazyLock};

use compact_calendar::CompactCalendar;
use flate2::bufread::DeflateDecoder;

use crate::ContextHolidays;

// Fetch generated code
pub use generated::*;

// --
// -- Errors
// --

/// Could not find input ISO code.
#[derive(Clone, Debug, Hash, PartialEq, Eq, PartialOrd, Ord)]
pub struct UnknownCountryCode(pub String);

impl std::fmt::Display for UnknownCountryCode {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Unknown ISO code `{}`", self.0)
    }
}

impl std::error::Error for UnknownCountryCode {}

// --
// -- Country Implems
// --

impl Country {
    /// Attempt to automatically detect a country from coordinates.
    ///
    /// ```
    /// use opening_hours::localization::{Coordinates, Country};
    ///
    /// let coords = Coordinates::new(48.86, 2.34).unwrap();
    /// let country_paris = Country::try_from_coords(coords).unwrap();
    /// assert_eq!(country_paris, Country::FR);
    /// ```
    #[cfg(feature = "auto-country")]
    pub fn try_from_coords(coords: crate::localization::Coordinates) -> Option<Self> {
        use country_boundaries::CountryBoundaries;
        use std::io::Read;

        static BOUNDARIES: LazyLock<CountryBoundaries> = LazyLock::new(|| {
            let mut buffer = Vec::new();

            DeflateDecoder::new(include_bytes!(env!("COUNTRY_BOUNDS_FILE")).as_slice())
                .read_to_end(&mut buffer)
                .expect("unable to parse country bounds data");

            CountryBoundaries::from_reader(buffer.as_slice())
                .expect("failed to load country boundaries database")
        });

        for cc in BOUNDARIES.ids(country_boundaries::LatLon::new(coords.lat(), coords.lon()).ok()?)
        {
            if let Ok(res) = cc.parse() {
                return Some(res);
            }
        }

        None
    }

    /// Load holidays for this country from a compact embedded database.
    ///
    /// ```
    /// use chrono::NaiveDate;
    /// use opening_hours::localization::Country;
    ///
    /// let holidays_fr = Country::FR.holidays();
    /// let date = NaiveDate::from_ymd_opt(2024, 7, 14).unwrap(); // french national day
    /// assert!(holidays_fr.get_public().contains(date));
    /// ```
    pub fn holidays(self) -> ContextHolidays {
        fn decode_holidays_db(
            countries: &'static str,
            encoded_data: &'static [u8],
        ) -> HashMap<Country, Arc<CompactCalendar>> {
            let mut reader = DeflateDecoder::new(encoded_data);

            countries
                .split(',')
                .filter_map(|region| {
                    let calendar = CompactCalendar::deserialize(&mut reader)
                        .expect("unable to parse holiday data");

                    let Ok(country) = region.parse() else {
                        #[cfg(feature = "log")]
                        log::warn!("Unknown initialized country code {region}");
                        return None;
                    };

                    Some((country, Arc::new(calendar)))
                })
                .collect()
        }

        static DB_PUBLIC: LazyLock<HashMap<Country, Arc<CompactCalendar>>> = LazyLock::new(|| {
            decode_holidays_db(
                env!("HOLIDAYS_PUBLIC_REGIONS"),
                include_bytes!(env!("HOLIDAYS_PUBLIC_FILE")),
            )
        });

        static DB_SCHOOL: LazyLock<HashMap<Country, Arc<CompactCalendar>>> = LazyLock::new(|| {
            decode_holidays_db(
                env!("HOLIDAYS_SCHOOL_REGIONS"),
                include_bytes!(env!("HOLIDAYS_SCHOOL_FILE")),
            )
        });

        ContextHolidays::new(
            DB_PUBLIC.get(&self).cloned().unwrap_or_default(),
            DB_SCHOOL.get(&self).cloned().unwrap_or_default(),
        )
    }
}
