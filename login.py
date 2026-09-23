from dash import html, dcc

login_layout = html.Div([
    html.Div([

        # 🔥 LEFT SIDE (BRANDING)
        html.Div([
            html.Img(
            src="/assets/Multicare2.png",className="login-logo"),
            html.H1("Multicare Hospital Analytics", className="main-heading"),
            html.P("Smart Healthcare Insight", className="main-subtext")
        ], className="login-left"),

        # 🔥 RIGHT SIDE (LOGIN FORM)
        html.Div([
             # Heading
            html.H2("Welcome Back", className="login-title"),

            # Subtitle
            html.P(
                "Please login to continue",className="login-subtitle"),


            dcc.Input(
                id="username",
                type="text",
                placeholder="Enter Username"
            ),

            dcc.Input(
                id="password",
                type="password",
                placeholder="Enter Password"
            ),

            html.Button( "🔐 Login", id="login-btn"),

            dcc.ConfirmDialog(
                id='error-popup',
                message='Invalid Username or Password'
            )

        ], className="login-right")

    ], className="login-box")

], className="login-container")