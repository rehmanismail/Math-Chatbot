from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def create_math_pdf(filename="math_reference_book.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=6
    )
    section_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0D9488"),
        spaceBefore=12,
        spaceAfter=5
    )
    code_box = ParagraphStyle(
        "CodeBox",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor("#1E293B"),
        backColor=colors.HexColor("#F8FAFC"),
        borderPadding=6,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#1F2937"),
        spaceAfter=5
    )

    story = []

    # Title Banner
    story.append(Paragraph("<b>Comprehensive Applied Mathematics & Engineering Handbook</b>", title_style))
    story.append(Paragraph("A master reference compendium containing core definitions, identities, and worked model solutions.", body_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1E3A8A"), spaceAfter=8))

    topics = [
        (
            "1. Differentiation & Differential Calculus",
            "<b>Fundamental Rules:</b><br/>"
            "• Power Rule: d/dx(x^n) = n*x^(n-1)<br/>"
            "• Product Rule: d/dx[u*v] = u'v + uv'<br/>"
            "• Quotient Rule: d/dx[u/v] = (u'v - uv') / v^2<br/>"
            "• Chain Rule: d/dx[f(g(x))] = f'(g(x)) * g'(x)<br/>"
            "• Derivatives of Transcendentals: d/dx(e^(ax)) = a*e^(ax), d/dx(ln x) = 1/x, d/dx(sin x) = cos x, d/dx(cos x) = -sin x, d/dx(tan x) = sec^2(x)<br/>"
            "<b>Model Problem:</b> Find the derivative of f(x) = x^2 * sin(3x).<br/>"
            "<b>Worked Solution:</b> Using product rule and chain rule:<br/>"
            "f'(x) = d/dx(x^2) * sin(3x) + x^2 * d/dx(sin(3x)) = 2x*sin(3x) + x^2*(3*cos(3x)) = 2x*sin(3x) + 3x^2*cos(3x)."
        ),
        (
            "2. Integral Calculus",
            "<b>Standard Integrals:</b><br/>"
            "• ∫ x^n dx = (x^(n+1))/(n+1) + C (for n ≠ -1); ∫ (1/x) dx = ln|x| + C<br/>"
            "• ∫ e^(ax) dx = (1/a)*e^(ax) + C; ∫ sin(ax) dx = -(1/a)*cos(ax) + C; ∫ cos(ax) dx = (1/a)*sin(ax) + C<br/>"
            "• Integration by Parts: ∫ u dv = u*v - ∫ v du<br/>"
            "<b>Model Problem:</b> Evaluate ∫ x * e^(2x) dx.<br/>"
            "<b>Worked Solution:</b> Let u = x (hence du = dx) and dv = e^(2x) dx (hence v = (1/2)*e^(2x)).<br/>"
            "∫ x*e^(2x) dx = x * ((1/2)*e^(2x)) - ∫ (1/2)*e^(2x) dx = (1/2)*x*e^(2x) - (1/4)*e^(2x) + C = (1/4)*e^(2x)*(2x - 1) + C."
        ),
        (
            "3. Laplace Transforms",
            "<b>Definition:</b> L{f(t)} = F(s) = ∫[0 to ∞] e^(-st) * f(t) dt.<br/>"
            "<b>Standard Transform Pairs:</b><br/>"
            "• L{1} = 1/s (s > 0)<br/>"
            "• L{t^n} = n! / s^(n+1) (n = 1, 2, 3...)<br/>"
            "• L{e^(at)} = 1 / (s - a)<br/>"
            "• L{sin(at)} = a / (s^2 + a^2); L{cos(at)} = s / (s^2 + a^2)<br/>"
            "• First Shifting Theorem: L{e^(at) * f(t)} = F(s - a)<br/>"
            "• Transform of Derivatives: L{y'(t)} = s*Y(s) - y(0); L{y''(t)} = s^2*Y(s) - s*y(0) - y'(0)<br/>"
            "<b>Model Problem:</b> Find the Laplace transform of f(t) = e^(3t) * cos(4t).<br/>"
            "<b>Worked Solution:</b> Since L{cos(4t)} = s / (s^2 + 16), by applying the first shifting theorem (replace s with s - 3):<br/>"
            "L{e^(3t) * cos(4t)} = (s - 3) / ((s - 3)^2 + 16) = (s - 3) / (s^2 - 6s + 25)."
        ),
        (
            "4. Differential Equations",
            "<b>First-Order Linear Differential Equation:</b> dy/dx + P(x)*y = Q(x)<br/>"
            "Integrating Factor: I(x) = exp(∫ P(x) dx). General Solution: y * I(x) = ∫ [Q(x) * I(x)] dx + C.<br/>"
            "<b>Second-Order Homogeneous DE with Constant Coefficients:</b> a*y'' + b*y' + c*y = 0.<br/>"
            "Characteristic Equation: a*r^2 + b*r + c = 0.<br/>"
            "• Distinct real roots (r1, r2): y(x) = c1*e^(r1*x) + c2*e^(r2*x)<br/>"
            "• Equal roots (r1 = r2 = r): y(x) = (c1 + c2*x)*e^(r*x)<br/>"
            "• Complex roots (α ± iβ): y(x) = e^(α*x) * [c1*cos(βx) + c2*sin(βx)]<br/>"
            "<b>Model Problem:</b> Solve y'' - 5y' + 6y = 0.<br/>"
            "<b>Worked Solution:</b> Characteristic equation: r^2 - 5r + 6 = 0 => (r - 2)(r - 3) = 0.<br/>"
            "Roots are r1 = 2, r2 = 3. General Solution: y(x) = c1*e^(2x) + c2*e^(3x)."
        ),
        (
            "5. Linear Algebra, Matrices & Complex Numbers",
            "<b>Determinant:</b> For A = [[a, b], [c, d]], det(A) = ad - bc.<br/>"
            "<b>Eigenvalues & Eigenvectors:</b> Solved using det(A - λI) = 0.<br/>"
            "<b>Complex Numbers:</b> z = a + ib = r*(cos θ + i*sin θ) = r*e^(iθ). Modulus: |z| = √(a^2 + b^2).<br/>"
            "<b>Model Problem:</b> Find eigenvalues of A = [[3, 1], [0, 2]].<br/>"
            "<b>Worked Solution:</b> det([[3 - λ, 1], [0, 2 - λ]]) = (3 - λ)(2 - λ) - 0 = 0. Eigenvalues are λ1 = 3, λ2 = 2."
        )
    ]

    for title, content in topics:
        story.append(Paragraph(f"<b>{title}</b>", section_style))
        story.append(Paragraph(content, code_box))
        story.append(Spacer(1, 3))

    doc.build(story)
    print(f"Successfully generated: {filename}")

if __name__ == "__main__":
    create_math_pdf()