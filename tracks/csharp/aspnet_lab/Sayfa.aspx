<%@ Page Language="C#" %>
<script runat="server">
void Yaz(string s) { System.IO.File.AppendAllText(Server.MapPath("~/olaylar.txt"), s + (IsPostBack ? " (postback)" : "") + "\n"); }
protected override void OnPreInit(EventArgs e) { Yaz("PreInit"); base.OnPreInit(e); }
protected override void OnInit(EventArgs e) { Yaz("Init"); base.OnInit(e); }
protected override void OnInitComplete(EventArgs e) { Yaz("InitComplete"); base.OnInitComplete(e); }
protected override void OnPreLoad(EventArgs e) { Yaz("PreLoad sayac=" + sayac.Text); base.OnPreLoad(e); }
protected override void OnLoad(EventArgs e) { if (!IsPostBack) sayac.Text = "0"; Yaz("Load sayac=" + sayac.Text); base.OnLoad(e); }
protected void Tikla(object s, EventArgs e) { sayac.Text = (int.Parse(sayac.Text) + 1).ToString(); Yaz("Click sayac=" + sayac.Text); }
protected override void OnLoadComplete(EventArgs e) { Yaz("LoadComplete"); base.OnLoadComplete(e); }
protected override void OnPreRender(EventArgs e) { Yaz("PreRender"); base.OnPreRender(e); }
protected override void OnSaveStateComplete(EventArgs e) { Yaz("SaveStateComplete"); base.OnSaveStateComplete(e); }
protected override void Render(HtmlTextWriter w) { Yaz("Render"); base.Render(w); }
protected override void OnUnload(EventArgs e) { Yaz("Unload"); base.OnUnload(e); }
</script>
<html><body><form id="f" runat="server">
<asp:Label id="sayac" runat="server" Text="0" />
<asp:Button id="dugme" runat="server" Text="Arttır" OnClick="Tikla" />
</form></body></html>
