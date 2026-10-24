using System;
using System.IO;
using System.Text;
using System.Web;
using System.Web.Hosting;

public class Istek : SimpleWorkerRequest {
    string fiil; byte[] govde;
    public Istek(string sayfa, string sorgu, TextWriter cikti, string fiil, string govde) : base(sayfa, sorgu, cikti) {
        this.fiil = fiil; this.govde = govde == null ? null : Encoding.UTF8.GetBytes(govde);
    }
    public override string GetHttpVerbName() { return fiil; }
    public override byte[] GetPreloadedEntityBody() { return govde; }
    public override bool IsEntireEntityBodyIsPreloaded() { return true; }
    public override string GetKnownRequestHeader(int i) {
        if (govde != null && i == HttpWorkerRequest.HeaderContentType) return "application/x-www-form-urlencoded";
        if (govde != null && i == HttpWorkerRequest.HeaderContentLength) return govde.Length.ToString();
        return base.GetKnownRequestHeader(i);
    }
}

public class Barindirici : MarshalByRefObject {
    public string Gonder(string sayfa, string sorgu, string fiil, string govde) {
        var sw = new StringWriter();
        HttpRuntime.ProcessRequest(new Istek(sayfa, sorgu, sw, fiil, govde));
        return sw.ToString();
    }
    public override object InitializeLifetimeService() { return null; }
}

