<%@ Application Language="C#" %>
<script runat="server">
void Y(string s) { if (Request.Path.EndsWith(".aspx")) System.IO.File.AppendAllText(Server.MapPath("~/olaylar.txt"), "[uygulama] " + s + "\n"); }
void Application_BeginRequest(object s, EventArgs e) { Y("BeginRequest"); }
void Application_AuthenticateRequest(object s, EventArgs e) { Y("AuthenticateRequest"); }
void Application_AuthorizeRequest(object s, EventArgs e) { Y("AuthorizeRequest"); }
void Application_PreRequestHandlerExecute(object s, EventArgs e) { Y("PreRequestHandlerExecute"); }
void Application_PostRequestHandlerExecute(object s, EventArgs e) { Y("PostRequestHandlerExecute"); }
void Application_EndRequest(object s, EventArgs e) { Y("EndRequest"); }
</script>
