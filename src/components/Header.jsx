export default function Header({theme,setTheme}){

    return(

        <div
            className="header"
            style={{position:"relative"}}
        >

            <button
                className="theme-btn"
                onClick={()=>setTheme(
                    theme==="dark" ? "light" : "dark"
                )}
            >

                {theme==="dark"
                    ? "☀ Light"
                    : "🌙 Dark"}

            </button>

            <h1>
                Gold Analyzer Pro
            </h1>

            <p>
                Smart Gold Market Analysis System
            </p>

        </div>

    );

}