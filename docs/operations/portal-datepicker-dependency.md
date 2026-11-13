# Portal Datepicker Dependency

Local runtime asset, not a CDN connection or npm runtime. Source:
[vanillajs-datepicker1.3.4](https://github.com/mymth/vanillajs-datepicker/tree/v1.3.4),
MIT license included verbatim as `datepicker-license.txt` in the Portal package.
Only Datepicker (not DateRangePicker) and German locale are shipped. Existing
Portal adapter owns range marking, strict date-only input and accessible focus;
the established library owns day/month rendering and selection. No drag support.

Public registry archive SHA-512 verified against npm metadata before extraction:
`c1a3b2a76032f8ad5503f07970d945812373151f5e7c254a6a8c8cc8d100840c2628bccc07d9c226ce95aa6a3a1ee1d603df151075db833e6d859ee11ffba884`.
No package scripts executed; only four exact archive members copied. Locale path
is `dist/js/locales/de.js`. No new network call or external font/image dependency
in the browser; CSP remains unchanged.

SHA-256 pins:

| File | SHA-256 |
| --- | --- |
| datepicker-v134.js | e41523183662ff9708cdda4d5d34de96b415303f161d7d0e7859bcee6f9d0ba4 |
| datepicker-de-v134.js | 841b3980a71ad33d56d8bd13e0e7eea0e5e3389413575ade92cc18f6f59487a4 |
| datepicker-v134.css | 15cb239e7e66edbd2382800ebeda386183d59106f9f56c968728177e5c987f00 |
| datepicker-license.txt | fc128e54c03aa96a27de02d0bb9c468a6869faca42c62942abcdffa25eaa3810 |

Dependency review is scoped, not an assertion of zero future vulnerabilities.
Typed German date + separate clocks remain the non-pointer alternative. Date
parser never normalizes invalid dates or changes Berlin/DST API semantics.
