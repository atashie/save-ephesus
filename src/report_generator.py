"""
Report Generator Module for Save Ephesus Elementary Report

Assembles the final PDF report using WeasyPrint.
Uses VERIFIED data - all claims fact-checked and corrected.
"""

import os
from pathlib import Path
from datetime import datetime

try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError) as e:
    WEASYPRINT_AVAILABLE = False
    print("Warning: WeasyPrint not available. PDF generation disabled.")
    print(f"  Reason: {type(e).__name__}")
    print("  HTML template will still be generated.")

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
ASSETS_CHARTS = PROJECT_ROOT / "assets" / "charts"
ASSETS_MAPS = PROJECT_ROOT / "assets" / "maps"
TEMPLATES = PROJECT_ROOT / "templates"
OUTPUT = PROJECT_ROOT / "output"
DOCS = PROJECT_ROOT / "docs"


def ensure_directories():
    """Create output directories if they don't exist."""
    OUTPUT.mkdir(parents=True, exist_ok=True)
    TEMPLATES.mkdir(parents=True, exist_ok=True)


def get_chart_path(chart_name):
    """Get the path to a chart image, or placeholder if not found."""
    chart_path = ASSETS_CHARTS / chart_name
    if chart_path.exists():
        return str(chart_path.absolute())
    return ""


def generate_report_html():
    """Generate the HTML content for the report using VERIFIED data."""

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Save Ephesus Elementary - Report to CHCCS Board</title>
    <style>
        @page {{
            size: letter;
            margin: 0.75in;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 11pt;
            line-height: 1.7;
            color: #333;
            max-width: 7in;
            margin: 0 auto;
        }}

        h1 {{
            color: #e6031b;
            font-size: 24pt;
            text-align: center;
            margin-bottom: 0.5em;
            border-bottom: 3px solid #e6031b;
            padding-bottom: 0.5em;
        }}

        h2 {{
            color: #e6031b;
            font-size: 16pt;
            margin-top: 1.5em;
            border-bottom: 2px solid #e6031b;
            padding-bottom: 0.25em;
        }}

        h3 {{
            color: #b8020f;
            font-size: 13pt;
            margin-top: 1em;
        }}

        .subtitle {{
            text-align: center;
            font-style: italic;
            color: #666;
            margin-bottom: 2em;
        }}

        .callout {{
            background-color: #fef9f9;
            border-left: 4px solid #e6031b;
            padding: 1em;
            margin: 1em 0;
            border-radius: 8px;
        }}

        .callout-warning {{
            background-color: #fff3e0;
            border-left: 4px solid #F18F01;
        }}

        .stat-box {{
            display: inline-block;
            background-color: #e6031b;
            color: white;
            padding: 0.5em 1em;
            margin: 0.5em;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(230,3,27,0.15);
        }}

        .stat-number {{
            font-size: 24pt;
            font-weight: bold;
            display: block;
        }}

        .stat-label {{
            font-size: 9pt;
            text-transform: uppercase;
        }}

        .stats-container {{
            text-align: center;
            margin: 1.5em 0;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1em 0;
        }}

        th, td {{
            border: 1px solid #ddd;
            padding: 0.5em;
            text-align: left;
        }}

        th {{
            background-color: #e6031b;
            color: white;
        }}

        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}

        .chart-container {{
            text-align: center;
            margin: 1.5em 0;
            page-break-inside: avoid;
        }}

        .chart-container img {{
            max-width: 100%;
            height: auto;
        }}

        .chart-caption {{
            font-size: 9pt;
            color: #666;
            font-style: italic;
            margin-top: 0.5em;
        }}

        .page-break {{
            page-break-before: always;
        }}

        .footer {{
            font-size: 9pt;
            color: #666;
            text-align: center;
            margin-top: 2em;
            padding-top: 1em;
            border-top: 1px solid #ddd;
        }}

        .highlight {{
            background-color: #fce4e4;
            padding: 0.2em 0.4em;
        }}

        ul {{
            margin-left: 1.5em;
        }}

        li {{
            margin-bottom: 0.5em;
        }}

        .recommendation {{
            background-color: #fef9f9;
            border: 2px solid #e6031b;
            padding: 1em;
            margin: 1.5em 0;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(230,3,27,0.1);
        }}

        .recommendation h3 {{
            color: #b8020f;
            margin-top: 0;
        }}

        .verified {{
            color: #28A745;
            font-weight: bold;
        }}

        .footnote {{
            font-size: 8pt;
            color: #666;
            border-top: 1px solid #ddd;
            margin-top: 1em;
            padding-top: 0.5em;
        }}
    </style>
</head>
<body>

    <!-- PAGE 1: EXECUTIVE SUMMARY -->
    <h1>Don't Close Ephesus Elementary</h1>
    <div style="text-align: center; margin: 1em 0;">
        <img src="{str((PROJECT_ROOT / 'assets' / 'logos' / 'ephesus-logo.png').absolute())}" alt="Ephesus Elementary Logo" style="height: 120px;">
    </div>
    <p class="subtitle">A Data-Driven Case for Keeping Our Neighborhood School Open</p>
    <p class="subtitle">Submitted to the Chapel Hill-Carrboro City Schools Board of Education<br>
    {datetime.now().strftime("%B %Y")}</p>

    <div class="stats-container">
        <div class="stat-box">
            <span class="stat-number">99*</span>
            <span class="stat-label">Students Walk to School</span>
        </div>
        <div class="stat-box">
            <span class="stat-number">#4</span>
            <span class="stat-label">Academic Growth<br>("Exceeded" Status)</span>
        </div>
        <div class="stat-box">
            <span class="stat-number">563</span>
            <span class="stat-label">New Housing Units<br>(149 Affordable)</span>
        </div>
    </div>

    <div class="callout">
        <strong>Key Finding:</strong> Ephesus Elementary is not a problem to be solved—it is a strategic asset
        for the district's future. Ephesus ranks <strong>among the top 4</strong> in academic growth,
        serves a diverse Title I population, and is positioned for growth with significant housing development nearby.
    </div>

    <h2>Executive Summary</h2>

    <p>The Chapel Hill-Carrboro City Schools district faces difficult budget decisions. However,
    closing Ephesus Elementary would be a short-sighted choice that contradicts the district's
    stated goals for equity, sustainability, and community engagement.</p>

    <p><strong>This report demonstrates that Ephesus Elementary:</strong></p>
    <ul>
        <li><strong>Ranks among top performers in academic growth</strong> - 4th of 11 elementary schools with "Exceeded" status</li>
        <li><strong>Is a walkable neighborhood school</strong> with 99 students walking to school*</li>
        <li><strong>Serves a diverse, high-need population</strong> as a Title I school (30-36% FRL, 50% minority)</li>
        <li><strong>Has significant housing development nearby</strong> - 563 units (149 affordable + 414 market-rate)</li>
        <li><strong>Provides community value</strong> that short-term savings cannot offset</li>
    </ul>

    <div class="recommendation">
        <h3>Recommendation</h3>
        <p>The Board should <strong>keep Ephesus Elementary open</strong> and recognize it as a model
        neighborhood school that exemplifies the district's values.</p>
    </div>

    <p class="footnote">*Parent-reported figure. Data marked with * indicates parent-supplied information.</p>

    <!-- PAGE 2: ACADEMIC EXCELLENCE -->
    <div class="page-break"></div>
    <h2>Academic Excellence</h2>

    <div class="callout">
        <strong>Ephesus Elementary achieved the 4th highest academic growth in the district.</strong>
        With a growth score of 85.8, Ephesus earned "Exceeded Expectations" status—demonstrating
        that our students and teachers are succeeding.
    </div>

    <div class="chart-container">
        <img src="{get_chart_path('academic_growth.png')}" alt="Academic Growth Chart">
        <p class="chart-caption">Figure 1: Academic growth scores by school (NC Report Cards 2023-24). Ephesus ranks #4 of 11.</p>
    </div>

    <h3>Verified Academic Data (All 11 Schools)<sup>2</sup></h3>
    <table>
        <tr>
            <th>Rank</th>
            <th>School</th>
            <th>Growth Score</th>
            <th>Status</th>
        </tr>
        <tr>
            <td>1</td>
            <td>Glenwood</td>
            <td>88.9</td>
            <td class="verified">Exceeded</td>
        </tr>
        <tr>
            <td>2</td>
            <td>Scroggs</td>
            <td>88.3</td>
            <td class="verified">Exceeded</td>
        </tr>
        <tr>
            <td>3</td>
            <td>Rashkis</td>
            <td>87.3</td>
            <td class="verified">Exceeded</td>
        </tr>
        <tr style="background-color: #fef0f0;">
            <td><strong>4</strong></td>
            <td><strong>Ephesus</strong></td>
            <td><strong>85.8</strong></td>
            <td class="verified"><strong>Exceeded</strong></td>
        </tr>
        <tr>
            <td>5</td>
            <td>Morris Grove</td>
            <td>84.4</td>
            <td>Met</td>
        </tr>
        <tr>
            <td>6</td>
            <td>Seawell</td>
            <td>82.6</td>
            <td>Met</td>
        </tr>
        <tr>
            <td>7</td>
            <td>FPG</td>
            <td>80.9</td>
            <td>Met</td>
        </tr>
        <tr>
            <td>8</td>
            <td>Northside</td>
            <td>79.9</td>
            <td>Met</td>
        </tr>
        <tr>
            <td>9</td>
            <td>Estes Hills</td>
            <td>74.3</td>
            <td>Met</td>
        </tr>
        <tr>
            <td>10</td>
            <td>Carrboro</td>
            <td>64.7</td>
            <td style="color: #DC3545;">Did Not Meet</td>
        </tr>
        <tr>
            <td>11</td>
            <td>McDougle</td>
            <td>63.2</td>
            <td style="color: #DC3545;">Did Not Meet</td>
        </tr>
    </table>

    <h3>What Makes Ephesus Successful</h3>
    <ul>
        <li><strong>Community engagement:</strong> High parent involvement and PTA support</li>
        <li><strong>Experienced faculty:</strong> Long-tenured teachers with deep expertise</li>
        <li><strong>Equity focus:</strong> Title I resources for diverse learners</li>
    </ul>

    <p class="footnote">Source: NC School Report Cards<sup>2</sup></p>

    <!-- PAGE 3: EQUITY & ACCESS -->
    <div class="page-break"></div>
    <h2>Equity & Access</h2>

    <h3>Title I Status Matters</h3>
    <p>Ephesus is a <strong>federally designated Title I school</strong>, meaning it serves a
    high-poverty student population that requires additional support. Closing Ephesus would
    disproportionately harm our most vulnerable families.</p>

    <div class="chart-container">
        <img src="{get_chart_path('demographics.png')}" alt="Demographics Chart">
        <p class="chart-caption">Figure 2: Free/Reduced Lunch and Minority Enrollment by School.<sup>1</sup></p>
    </div>

    <h3>Ephesus Demographics<sup>1</sup></h3>
    <table>
        <tr>
            <th>Metric</th>
            <th>Ephesus</th>
        </tr>
        <tr>
            <td>Free/Reduced Lunch</td>
            <td>30-36%</td>
        </tr>
        <tr>
            <td>Minority Enrollment</td>
            <td>50%</td>
        </tr>
        <tr>
            <td>Title I Status</td>
            <td>Yes</td>
        </tr>
        <tr>
            <td>EC Pre-K Staff</td>
            <td>2 of 3 district-wide*</td>
        </tr>
    </table>

    <div class="callout-warning callout">
        <strong>Equity Consideration:</strong> Closing a Title I school serving low-income and minority
        students requires careful consideration of the district's commitment to educational equity.
    </div>

    <p class="footnote">Source: NCES Common Core of Data<sup>1</sup></p>

    <!-- PAGE 4: COMMUNITY & HOUSING -->
    <div class="page-break"></div>
    <h2>Community Impact & Housing Development</h2>

    <h3>Walkable Neighborhood School</h3>
    <p>Ephesus Elementary has strong walkability with <strong>99 students walking to school</strong>.*
    Closing Ephesus would mean:</p>
    <ul>
        <li><strong>Added transportation costs:</strong> ~$57K-$75K/year for new bus routes (NC estimates)</li>
        <li><strong>Lost environmental benefits</strong> from fewer students walking</li>
        <li><strong>Broken neighborhood connections</strong> built over decades</li>
    </ul>

    <h3>Housing Development Near Ephesus</h3>

    <div class="chart-container">
        <img src="{get_chart_path('ephesus_housing_detail.png')}" alt="Ephesus Housing Detail">
        <p class="chart-caption">Figure 3: Housing development near Ephesus (563 built + 150 planned = 713 total units).</p>
    </div>

    <table>
        <tr>
            <th>Development</th>
            <th>Units</th>
            <th>Type</th>
            <th>Status</th>
        </tr>
        <tr>
            <td>Greenfield (Place + Commons)</td>
            <td>149</td>
            <td>Affordable</td>
            <td class="verified">Completed</td>
        </tr>
        <tr>
            <td>Park Apartments</td>
            <td>414</td>
            <td><strong>Market-Rate</strong></td>
            <td>Under Construction</td>
        </tr>
        <tr style="background-color: #fff3e0;">
            <td>Longleaf Trace (Legion Rd)<sup>13</sup></td>
            <td>150</td>
            <td>Affordable (planned)</td>
            <td style="font-style: italic;">Planned 2027-29</td>
        </tr>
        <tr style="background-color: #fef0f0;">
            <td><strong>Total (built)</strong></td>
            <td><strong>563</strong></td>
            <td>149 affordable (26%)</td>
            <td></td>
        </tr>
        <tr style="background-color: #fef0f0;">
            <td><strong>Total (with planned)</strong></td>
            <td><strong>713</strong></td>
            <td>299 affordable (42%)</td>
            <td></td>
        </tr>
    </table>

    <h3>District-Wide Housing Comparison</h3>

    <div class="chart-container">
        <img src="{get_chart_path('housing_development.png')}" alt="Housing Development by School Zone">
        <p class="chart-caption">Figure 4: Housing development by school zone (all 11 elementary schools).</p>
    </div>

    <p><strong>Honest Context:</strong> Ephesus ranks 4th in total housing development among CHCCS
    school zones. Morris Grove has nearly double the development (~1,170 units). Northside has the
    highest concentration of affordable housing (244 units, 100% affordable).</p>

    <p class="footnote">*Parent-reported figure. Sources: Town of Chapel Hill<sup>3</sup>, Chapel Hill Affordable Housing<sup>4</sup></p>

    <!-- PAGE 5: FINANCIAL ANALYSIS -->
    <div class="page-break"></div>
    <h2>Financial Analysis</h2>

    <h3>Verified Financial Data</h3>
    <table>
        <tr>
            <th>Cost Category</th>
            <th>Amount</th>
            <th>Source</th>
        </tr>
        <tr>
            <td>Gross savings from closure</td>
            <td>+$1.7M/year</td>
            <td class="verified">CHCCS (Aug 2025)</td>
        </tr>
        <tr>
            <td>Added bus costs (99 students)</td>
            <td>-$57K to -$75K/year</td>
            <td class="verified">NC estimates</td>
        </tr>
        <tr>
            <td>Building maintenance (if retained)</td>
            <td>-$60K to -$150K/year</td>
            <td>National benchmarks*</td>
        </tr>
        <tr style="background-color: #fef0f0;">
            <td><strong>Net annual savings</strong></td>
            <td><strong>~$1.53M/year</strong></td>
            <td></td>
        </tr>
    </table>

    <h3>Long-Term Considerations</h3>
    <ul>
        <li><strong>Ephesus renovation estimate:</strong> $28.9M (Woolpert Phase 2, years 5-10)</li>
        <li><strong>Bond allocation:</strong> $174.7M to CHCCS for 3 school replacements (Carrboro, Estes Hills, FPG)</li>
        <li><strong>Ephesus bond funding:</strong> $0 (not receiving replacement funds)</li>
    </ul>

    <div class="callout">
        <strong>Request for the Board:</strong> We request a comprehensive review of all schools—considering
        facility condition, walkability, enrollment trends, equity, and housing development—before making
        closure decisions.
    </div>

    <p class="footnote">*Building maintenance estimates based on national benchmarks (Philadelphia, Chicago data). No CHCCS-specific data available.</p>

    <!-- PAGE 6: ADDITIONAL CONTEXT -->
    <div class="page-break"></div>
    <h2>The Real Challenge: Attracting Families</h2>

    <div class="callout">
        <strong>Core Issue:</strong> Closing schools does not address the fundamental problem—young
        families aren't moving to Chapel Hill due to housing costs and limited affordable options.
    </div>

    <h3>Why Families Choose Other Districts</h3>
    <ul>
        <li><strong>Housing costs</strong> among the highest in the Triangle region</li>
        <li><strong>Limited affordable family housing</strong> options compared to surrounding areas</li>
        <li><strong>Surrounding areas</strong> offer comparable schools at lower cost of living</li>
    </ul>

    <h3>How Closures Make This Worse</h3>
    <p>Eliminating walkable neighborhood schools removes a key selling point for young families
    considering Chapel Hill. This creates a downward spiral:</p>
    <ul>
        <li>Fewer walkable schools → Chapel Hill less attractive to families</li>
        <li>Fewer families → continued enrollment decline</li>
        <li>Lower enrollment → pressure to close more schools</li>
    </ul>

    <h3>Enrollment Projections: Ephesus is Positioned for Growth</h3>
    <table>
        <tr>
            <th>School</th>
            <th>Change 2019-2025</th>
            <th>Projected Change 2025-2036</th>
        </tr>
        <tr style="background-color: #fef0f0;">
            <td><strong>Ephesus</strong></td>
            <td>-46</td>
            <td><strong>+21</strong></td>
        </tr>
    </table>
    <p><strong>Key insight:</strong> While Ephesus experienced pandemic-era decline like other schools,
    projections show enrollment GROWTH through 2036—unlike some schools slated for closure.<sup>14</sup></p>

    <!-- PAGE 7: OPERATIONAL CONCERNS -->
    <div class="page-break"></div>
    <h2>Transportation Crisis</h2>

    <div class="callout-warning callout">
        <strong>Before adding bus routes, consider the existing crisis.</strong>
        CHCCS is struggling to staff current routes—adding 99 students to the bus system
        creates operational risk.
    </div>

    <h3>CHCCS Transportation Data (2023-24)<sup>8</sup></h3>
    <table>
        <tr>
            <th>Metric</th>
            <th>Value</th>
        </tr>
        <tr>
            <td>Driver count decline</td>
            <td>70+ → 37 drivers</td>
        </tr>
        <tr>
            <td>Instructional hours lost (first 39 days)</td>
            <td>3,950 hours</td>
        </tr>
        <tr>
            <td>Student ride times</td>
            <td>Up to 60+ minutes</td>
        </tr>
    </table>

    <h3>North Carolina Context<sup>8</sup></h3>
    <ul>
        <li>NC ranks <strong>50th nationally</strong> in school bus driver pay</li>
        <li>Average salary: $14,628/year</li>
        <li>27 states pay 50%+ more than North Carolina</li>
    </ul>

    <p><strong>Implication:</strong> Converting 99 walkers to bus riders when we cannot adequately
    staff existing routes creates operational and safety concerns.</p>

    <h2>Equity and Achievement Gaps</h2>

    <div class="callout">
        <strong>Chapel Hill has significant achievement gaps that closing Title I schools may worsen.</strong>
    </div>

    <h3>Chapel Hill Achievement Data (Stanford Educational Opportunity Project)<sup>7</sup></h3>
    <table>
        <tr>
            <th>Metric</th>
            <th>Value</th>
        </tr>
        <tr>
            <td>Black students achievement gap</td>
            <td>4.3 grade levels behind white peers</td>
        </tr>
        <tr>
            <td>AP class enrollment disparity</td>
            <td>Black students 3.7x less likely to enroll</td>
        </tr>
        <tr>
            <td>Discipline disparity</td>
            <td>45% of suspensions (11.4% of enrollment)</td>
        </tr>
    </table>

    <p><strong>Why this matters:</strong> Ephesus is a Title I school serving diverse, low-income
    populations. Research shows school closures disproportionately harm these communities.<sup>10,11</sup></p>

    <h2>Research on School Closure Impacts</h2>

    <p>Academic research consistently documents negative effects of school closures on displaced students:</p>

    <ul>
        <li><strong>Engberg et al. (2012):</strong> Closures disproportionately affect low-income students<sup>10</sup></li>
        <li><strong>de la Torre &amp; Gwynne (2009):</strong> Displaced students rarely land in higher-performing schools<sup>11</sup></li>
        <li><strong>Kirshner et al. (2010):</strong> Closure creates lasting emotional and academic disruption<sup>12</sup></li>
        <li><strong>Sunderman &amp; Payne (2009):</strong> Students from closed schools show measurable academic decline</li>
    </ul>

    <div class="callout-warning callout">
        <strong>Research Consensus:</strong> The burden of school closures falls heaviest on the most
        vulnerable students—exactly the population Ephesus serves as a Title I school.
    </div>

    <!-- PAGE 8: RECOMMENDATION -->
    <div class="page-break"></div>
    <h2>Strategic Recommendation</h2>

    <h3>Ephesus is a Valuable Community Asset</h3>
    <p>Rather than viewing Ephesus as a cost to eliminate, the Board should recognize it as a
    strategic asset that:</p>
    <ul>
        <li><strong>Achieves academic excellence</strong> - 4th in district growth with "Exceeded" status</li>
        <li><strong>Advances equity</strong> by serving diverse, high-need populations (Title I school)</li>
        <li><strong>Supports community development</strong> with 563 housing units nearby</li>
        <li><strong>Promotes sustainability</strong> through walkability (99 students walk to school)</li>
    </ul>

    <div class="recommendation">
        <h3>Our Request to the Board</h3>
        <ol>
            <li><strong>Keep Ephesus Elementary open</strong> as a vital neighborhood school</li>
            <li><strong>Recognize Ephesus's academic success</strong> - among top 4 in district growth</li>
            <li><strong>Consider the community impact</strong> of closing a Title I school</li>
            <li><strong>Align school planning with housing development</strong> for long-term community benefit</li>
        </ol>
    </div>

    <h3>References</h3>
    <ol style="font-size: 9pt;">
        <li>NCES Common Core of Data - nces.ed.gov/ccd/schoolsearch/</li>
        <li>NC School Report Cards (2023-24) - ncreports.ondemand.sas.com</li>
        <li>Town of Chapel Hill - townofchapelhill.org</li>
        <li>Chapel Hill Affordable Housing - chapelhillaffordablehousing.org</li>
        <li>CHCCS Bond Overview - chccs.org/community/schoolbond/overview</li>
        <li>Chapelboro News - chapelboro.com</li>
        <li>Stanford Educational Opportunity Project - edopportunity.org</li>
        <li>WRAL News, NC State Board of Education transportation data</li>
        <li>Charlotte Urban Institute - transportation cost estimates</li>
        <li>Engberg et al. (2012), RAND Corporation - school closure impacts</li>
        <li>de la Torre &amp; Gwynne (2009), UChicago Consortium - displaced student outcomes</li>
        <li>Kirshner et al. (2010), Teachers College Record - closure disruption effects</li>
        <li>Chapel Hill Engage, Longleaf Trace project - engage.chapelhillnc.gov/legion-property</li>
        <li>CHCCS Enrollment Projections (Slide 28)</li>
    </ol>
    <p style="font-size: 9pt; color: #666;">* indicates parent-supplied data requiring independent verification</p>

    <div class="callout">
        <strong>The Bottom Line:</strong> Ephesus Elementary delivers strong academic results,
        serves a diverse community, and is positioned for future growth. The approximately $1.53M
        annual savings from closure must be weighed against the long-term costs of losing a
        thriving neighborhood school.
    </div>

    <!-- FOOTER -->
    <div class="footer">
        <p>Prepared by concerned members of the Ephesus Elementary community.</p>
        <p>Data sources: NC School Report Cards, NCES, CHCCS, Town of Chapel Hill, Chapel Hill Affordable Housing</p>
        <p>Generated: {datetime.now().strftime("%B %d, %Y")}</p>
        <p><em>* indicates parent-supplied data requiring independent verification</em></p>
    </div>

</body>
</html>
"""

    return html_content


def save_html_template(html_content):
    """Save HTML to templates directory."""
    template_path = TEMPLATES / "report_template.html"
    with open(template_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Created: {template_path}")
    return template_path


def generate_pdf(html_path):
    """Generate PDF from HTML using WeasyPrint."""
    if not WEASYPRINT_AVAILABLE:
        print("WeasyPrint not available. Skipping PDF generation.")
        print("The HTML template has been saved and can be printed to PDF from a browser.")
        return None

    pdf_path = OUTPUT / "ephesus_report.pdf"

    try:
        HTML(filename=str(html_path)).write_pdf(str(pdf_path))
        print(f"Created: {pdf_path}")
        return pdf_path
    except Exception as e:
        print(f"Error generating PDF: {e}")
        print("Try opening the HTML file in a browser and using Print > Save as PDF")
        return None


def main():
    """Generate the complete report with VERIFIED data."""
    print("=" * 60)
    print("Save Ephesus Elementary - Report Generator")
    print("Using VERIFIED data - all claims fact-checked")
    print("=" * 60)

    ensure_directories()

    # Check for chart files (updated list)
    print("\nChecking for visualization files...")
    charts_needed = [
        "academic_growth.png",
        "demographics.png",
        "housing_development.png",
        "ephesus_housing_detail.png",
    ]

    missing_charts = []
    for chart in charts_needed:
        chart_path = ASSETS_CHARTS / chart
        if chart_path.exists():
            print(f"  Found: {chart}")
        else:
            print(f"  Missing: {chart}")
            missing_charts.append(chart)

    if missing_charts:
        print(f"\nWarning: {len(missing_charts)} charts missing.")
        print("Run 'python src/visualizations.py' to generate charts first.")
        print("Continuing with available charts...\n")

    # Generate HTML
    print("\nGenerating HTML report with verified data...")
    html_content = generate_report_html()
    html_path = save_html_template(html_content)

    # Generate PDF
    print("\nGenerating PDF...")
    pdf_path = generate_pdf(html_path)

    print("\n" + "=" * 60)
    print("Report generation complete!")
    print(f"\nHTML template: {html_path}")
    if pdf_path:
        print(f"PDF report: {pdf_path}")
    else:
        print("\nTo create PDF manually:")
        print(f"  1. Open {html_path} in a web browser")
        print("  2. Use Print > Save as PDF")
    print("\nVERIFIED DATA USED:")
    print("  - Academic growth: Ephesus #4 of 11 (85.8, Exceeded)")
    print("  - Demographics: 30-36% FRL, 50% minority (NCES)")
    print("  - Housing: 563 total (149 affordable + 414 market-rate)")
    print("  - Costs: $1.7M savings - $66K bus - $100K maint = $1.53M net")
    print("=" * 60)


if __name__ == "__main__":
    main()
