"""
pyap.source_GB.data
~~~~~~~~~~~~~~~~~~~~

This module provides regular expression definitions required for
detecting British/GB/UK addresses.

The module is expected to always contain 'full_address' variable containing
all address parsing definitions.

:copyright: (c) 2015 by Vladimir Goncharov.
:license: MIT, see LICENSE for more details.
"""

"""Numerals from one to nine
Note: here and below we use syntax like '[Oo][Nn][Ee]'
instead of '(one)(?i)' to match 'One' or 'oNe' because
Python Regexps don't seem to support turning On/Off
case modes for subcapturing groups.
"""
zero_to_nine = r"""
(?:
    [Zz][Ee][Rr][Oo]\s|[Oo][Nn][Ee]\s|[Tt][Ww][Oo]\s|
    [Tt][Hh][Rr][Ee][Ee]\s|[Ff][Oo][Uu][Rr]\s|
    [Ff][Ii][Vv][Ee]\s|[Ss][Ii][Xx]\s|
    [Ss][Ee][Vv][Ee][Nn]\s|[Ee][Ii][Gg][Hh][Tt]\s|
    [Nn][Ii][Nn][Ee]\s|[Tt][Ee][Nn]\s|
    [Ee][Ll][Ee][Vv][Ee][Nn]\s|
    [Tt][Ww][Ee][Ll][Vv][Ee]\s|
    [Tt][Hh][Ii][Rr][Tt][Ee][Ee][Nn]\s|
    [Ff][Oo][Uu][Rr][Tt][Ee][Ee][Nn]\s|
    [Ff][Ii][Ff][Tt][Ee][Ee][Nn]\s|
    [Ss][Ii][Xx][Tt][Ee][Ee][Nn]\s|
    [Ss][Ee][Vv][Ee][Nn][Tt][Ee][Ee][Nn]\s|
    [Ee][Ii][Gg][Hh][Tt][Ee][Ee][Nn]\s|
    [Nn][Ii][Nn][Ee][Tt][Ee][Ee][Nn]\s
)
"""

# Numerals - 10, 20, 30 ... 90
ten_to_ninety = r"""
(?:
    [Tt][Ee][Nn]\s|[Tt][Ww][Ee][Nn][Tt][Yy]\s|
    [Tt][Hh][Ii][Rr][Tt][Yy]\s|
    [Ff][Oo][Rr][Tt][Yy]\s|
    [Ff][Oo][Uu][Rr][Tt][Yy]\s|
    [Ff][Ii][Ff][Tt][Yy]\s|[Ss][Ii][Xx][Tt][Yy]\s|
    [Ss][Ee][Vv][Ee][Nn][Tt][Yy]\s|
    [Ee][Ii][Gg][Hh][Tt][Yy]\s|
    [Nn][Ii][Nn][Ee][Tt][Yy]\s
)
"""

# One hundred
hundred = r"""
(?:
    [Hh][Uu][Nn][Dd][Rr][Ee][Dd]\s
)
"""

# One thousand
thousand = r"""
(?:
    [Tt][Hh][Oo][Uu][Ss][Aa][Nn][Dd]\s
)
"""

part_divider = r"(?: [\,\s\.\-]{0,3}\,[\,\s\.\-]{0,3} )"
space_pattern = r"(?: [\s\t]{1,3} )"  # TODO: use \b for word boundary

"""
Regexp for matching street number.
Street number can be written 2 ways:
1) Using letters - "One thousand twenty two"
2) Using numbers
   a) - "1022"
   b) - "85-1190"
   c) - "85 1190"
"""
street_number = r"""
(?P<street_number>
    (?:
        (?:
            [Nn][Uu][Mm][Bb][Ee][Rr]|
            [Nn][RrOo]\.?|
            [Nn][Uu][Mm]\.?|
            #
        )
        {space}?
    )?
    (?:
        (?:
            [Aa][Nn][Dd]\s
            |
            {thousand} 
            |
            {hundred} 
            |
            {zero_to_nine} 
            |
            {ten_to_ninety} 
        ){from_to}
        |
        (?:
            \d{from_to}
            (?: {space}? [A-Za-z] (?![A-Za-z\d]]) )?
            (?!\d)
            (?:{space}?\-{space}?\d{from_to} (?: {space}? [A-Za-z] (?![A-Za-z\d]) )? )?
        )
    )
    {space}?
)  # end street_number
""".format(
    thousand=thousand,
    hundred=hundred,
    zero_to_nine=zero_to_nine,
    ten_to_ninety=ten_to_ninety,
    space=space_pattern,
    from_to="{1,5}",
)

"""
Regexp for matching street name.
In "Hoover Boulevard", "Hoover" is a street name
Seems like the longest US street is 'Northeast Kentucky Industrial Parkway',
which is 31 charactors
https://atkinsbookshelf.wordpress.com/tag/longest-street-name-in-us/
"""
street_name = r"""
(?P<street_name>
    (?(street_number)           # If street_number has been found, then digits
                                # can be in the street otherwise no digits are
        [a-zA-Z0-9\s\.]{3,31}   # allowed. This aims to prevent street_name
        |                       # matching everything before the address as
        [a-zA-Z\s\.]{3,31}      # well as the number.
    )
)
"""

post_direction = r"""
(?P<post_direction>
    (?:
        [Nn][Oo][Rr][Tt][Hh]\s|
        [Ss][Oo][Uu][Tt][Hh]\s|
        [Ee][Aa][Ss][Tt]\s |
        [Ww][Ee][Ss][Tt]\s 
    )
    |
    (?:
        NW\s|NE\s|SW\s|SE\s
    )
    |
    (?:
        N\.?\s|S\.?\s|E\.?\s|W\.?\s
    )
)  # end post_direction
"""

# Regexp for matching street type
street_type = r"""
(?:
    (?P<street_type>
        # Street
        [Ss][Tt][Rr][Ee][Ee][Tt]|S[Tt]\.?(?![A-Za-z])|
        # Boulevard
        [Bb][Oo][Uu][Ll][Ee][Vv][Aa][Rr][Dd]|[Bb][Ll][Vv][Dd]\.?|
        # Highway
        [Hh][Ii][Gg][Hh][Ww][Aa][Yy]|H[Ww][Yy]\.?|
        # Broadway
        [Bb][Rr][Oo][Aa][Dd][Ww][Aa][Yy]|
        # Freeway
        [Ff][Rr][Ee][Ee][Ww][Aa][Yy]|
        # Causeway
        [Cc][Aa][Uu][Ss][Ee][Ww][Aa][Yy]|C[Ss][Ww][Yy]\.?|
        # Expressway
        [Ee][Xx][Pp][Rr][Ee][Ss][Ss][Ww][Aa][Yy]|
        # Way
        [Ww][Aa][Yy]|
        # Walk
        [Ww][Aa][Ll][Kk]|
        # Lane
        [Ll][Aa][Nn][Ee]|L[Nn]\.?|
        # Road
        [Rr][Oo][Aa][Dd]|R[Dd]\.?|
        # Avenue
        [Aa][Vv][Ee][Nn][Uu][Ee]|A[Vv][Ee]\.?|
        # Circle
        [Cc][Ii][Rr][Cc][Ll][Ee]|C[Ii][Rr]\.?|
        # Cove
        [Cc][Oo][Vv][Ee]|C[Vv]\.?|
        # Drive
        [Dd][Rr][Ii][Vv][Ee]|D[Rr]\.?|
        # Parkway
        [Pp][Aa][Rr][Kk][Ww][Aa][Yy]|P[Kk][Ww][Yy]\.?|
        # Park
        [Pp][Aa][Rr][Kk]|
        # Court
        [Cc][Oo][Uu][Rr][Tt]|C[Tt]\.?|
        # Square
        [Ss][Qq][Uu][Aa][Rr][Ee]|S[Qq]\.?|
        # Loop
        [Ll][Oo][Oo][Pp]|L[Pp]\.?|
        # Place
        [Pp][Ll][Aa][Cc][Ee]|P[Ll]\.?|
        # Parade
        [Pp][Aa][Rr][Aa][Dd][Ee]|P[Ll]\.?|
        # Estate
        [Ee][Ss][Tt][Aa][Tt][Ee]
    )
    (?P<route_id>)
)  # end street_type
"""

floor = r"""
(?P<floor>
    (?:
    \d+[A-Za-z]{0,2}\.?\s[Ff][Ll][Oo][Oo][Rr]\s
    )
    |
    (?:
        [Ff][Ll][Oo][Oo][Rr]\s\d+[A-Za-z]{0,2}\s
    )
)  # end floor
"""

building = rf"""
(?P<building_id>
    (?:
        (?:[Bb][Uu][Ii][Ll][Dd][Ii][Nn][Gg])
        |
        (?:[Bb][Ll][Dd][Gg])
    )
    \s
    (?:
        (?:
            [Aa][Nn][Dd]\s
            |
            {thousand}
            |
            {hundred}
            |
            {zero_to_nine}
            |
            {ten_to_ninety}
        ){{1,5}}
        |
        \d{{0,4}}[A-Za-z]?
    )
    \s ?
)  # end building_id
"""

occupancy = rf"""
(?P<occupancy>
    (?:
        (?:
            # Suite
            [Ss][Uu][Ii][Tt][Ee]|[Ss][Tt][Ee]\.?
            |
            # Studio
            [Ss][Tt][Uu][Dd][Ii][Oo]|[Ss][Tt][UuDd]\.?
            |
            # Apartment
            [Aa][Pp][Tt]\.?|[Aa][Pp][Aa][Rr][Tt][Mm][Ee][Nn][Tt]
            |
            # Room
            [Rr][Oo][Oo][Mm]|[Rr][Mm]\.?
            |
            # Flat
            [Ff][Ll][Aa][Tt]
            |
            \#
        )
        {space_pattern}?
        (?:
            [A-Za-z\#\&\-\d]{{1,7}}
        )?
    )
    {space_pattern}?
)  # end occupancy
"""

po_box = rf"""
(?:
    [Pp]\.? {space_pattern}? [Oo]\.? {space_pattern}? ([Bb][Oo][Xx]{space_pattern}?)?\d+
)
"""

# TODO: maybe remove the '?' on the part_dividers is mismatch address parts
full_street = rf"""
(?:
    (?P<full_street>

        (?:
            {po_box} {part_divider}?
        )?
        (?:
            {floor} {part_divider}?
        )?
        (?:
            {occupancy} {part_divider}?
        )?
        (?:
            {building} {part_divider}?
        )?

        (?:
            (?: {street_number} {space_pattern} )
            |
            (?! \d{{}} )

        )?
        (?:{street_name} )
        (?:{space_pattern} {street_type} {space_pattern}?)?
    )
)  # end full_street
"""

# region1 is actually a "state"
region1 = r"""
(?P<region1>
    [A-Za-z]{1}[a-zA-Z0-9\s\.\-']{1,35}
)  # end region1
"""

city = r"""
(?P<city>
    [A-Za-z]{1}[a-zA-Z0-9\s\.\-']{1,35}
)  # end city
"""

postal_code = r"""
(?P<postal_code>
    (?:  # Mainland British postcodes
        (?:
            (?:\b[Ww][Cc][0-9][abehmnprvwxyABEHMNPRVWXY])|
            (?:\b[Ee][Cc][1-4][abehmnprvwxyABEHMNPRVWXY])|
            (?:\b[Nn][Ww]1[Ww])|
            (?:\b[Ss][Ee]1[Pp])|
            (?:\b[Ss][Ww]1[abehmnprvwxyABEHMNPRVWXY])|
            (?:\b[EeNnWw]1[a-hjkpstuwA-HJKPSTUW])|
            (?:\b[BbEeGgLlMmNnSsWw][0-9][0-9]?)|
            (?:\b[a-pr-uwyzA-PR-UWYZ][a-hk-yxA-HK-XY][0-9][0-9]?)
        )
        \s{0,}[0-9][abd-hjlnp-uw-zABD-HJLNP-UW-Z]{2}
    )
)  # end postal_code
"""

country = r"""
(?P<country>
    (?:[Tt][Hh][Ee]\s*)?[Uu][Nn][Ii][Tt][Ee][Dd]\s*[Kk][Ii][Nn][Gg][Dd][Oo][Mm]\s*[Oo][Ff]\s*(?:[Gg][Rr][Ee][Aa][Tt]\s*)?[Bb][Rr][Ii][Tt][Aa][Ii][Nn](?:\s*[Aa][Nn][Dd]\s*[Nn][Oo][Rr][Tt][Hh][Ee][Rr][Nn]\s*[Ii][Rr][Ee][Ll][Aa][Nn][Dd])?|
    (?:[Gg][Rr][Ee][Aa][Tt]\s*)?[Bb][Rr][Ii][Tt][Aa][Ii][Nn](?:\s*[Aa][Nn][Dd]\s*[Nn][Oo][Rr][Tt][Hh][Ee][Rr][Nn]\s*[Ii][Rr][Ee][Ll][Aa][Nn][Dd])?|
    (?:[Tt][Hh][Ee]\s*)?[Uu][Nn][Ii][Tt][Ee][Dd]\s*[Kk][Ii][Nn][Gg][Dd][Oo][Mm]|
    (?:[Nn][Oo][Rr][Tt][Hh][Ee][Rr][Nn]\s*)?[Ii][Rr][Ee][Ll][Aa][Nn][Dd]|
    [Ee][Nn][Gg][Ll][Aa][Nn][Dd]|
    [Ss][Cc][Oo][Tt][Ll][Aa][Nn][Dd]|
    [Ww][Aa][Ll][Ee][Ss]|
    [Cc][Yy][Mm][Rr][Uu]|
    [Gg][Bb]|
    [Uu][Kk]|
    [Nn]\.?\s*[Ii]\.?
)  # end country
"""

full_address = rf"""
(?P<full_address>
    {full_street}
    (?: {part_divider} {city} )?
    (?: {part_divider} {region1} )?
    {part_divider}? {postal_code}
    (?: {part_divider} {country} )?
)  # end full_address
"""
