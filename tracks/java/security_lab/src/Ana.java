package pafta.security;
import java.util.*;
import org.springframework.context.annotation.*;
import org.springframework.aop.support.AopUtils;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.authorization.*;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.access.intercept.RequestMatcherDelegatingAuthorizationManager;
import org.springframework.security.web.servlet.util.matcher.PathPatternRequestMatcher;
import org.springframework.security.web.util.matcher.AnyRequestMatcher;
public class Ana {
 public static Authentication user(String name,String authority){return UsernamePasswordAuthenticationToken.authenticated(name,"unused",List.of(new SimpleGrantedAuthority(authority)));}
 public static String decide(RequestMatcherDelegatingAuthorizationManager manager,Authentication auth,String path){
  var req=new MockHttpServletRequest("GET",path);req.setServletPath(path);
  return manager.authorize(()->auth,req).isGranted()?"IZIN":"RED";
 }
 public static class Servis {
  @PreAuthorize("hasAuthority('RAPOR_OKU')") public String rapor(){return "rapor";}
  public String dolayli(){return rapor();}
  @PreAuthorize("#sahip == authentication.name") public String belge(String sahip){return "belge:"+sahip;}
 }
 @Configuration @EnableMethodSecurity public static class Config {@Bean public Servis servis(){return new Servis();}}
 interface Work {String run();}
 static String call(Work work){try{return "OK "+work.run();}catch(Exception e){return "RED "+e.getClass().getSimpleName();}}
 public static void main(String[] args){
  var pp=PathPatternRequestMatcher.withDefaults();
  var a=RequestMatcherDelegatingAuthorizationManager.builder().add(pp.matcher("/yonetim/**"),AuthorityAuthorizationManager.hasAuthority("YONETICI")).add(AnyRequestMatcher.INSTANCE,AuthenticatedAuthorizationManager.authenticated()).build();
  var b=RequestMatcherDelegatingAuthorizationManager.builder().add(AnyRequestMatcher.INSTANCE,AuthenticatedAuthorizationManager.authenticated()).add(pp.matcher("/yonetim/**"),AuthorityAuthorizationManager.hasAuthority("YONETICI")).build();
  var ayse=user("ayse","RAPOR_OKU");var mdr=user("mdr","YONETICI");
  System.out.println("--- zincir A: /yonetim/** once, /** sonra ---");
  System.out.println("ayse[RAPOR_OKU] GET /yonetim/sil -> "+decide(a,ayse,"/yonetim/sil"));
  System.out.println("mdr[YONETICI]   GET /yonetim/sil -> "+decide(a,mdr,"/yonetim/sil"));
  for(String path:List.of("/yonetim","/yonetimsil","/Yonetim/sil","/rapor"))System.out.println("ayse[RAPOR_OKU] GET "+String.format("%-12s",path)+" -> "+decide(a,ayse,path));
  System.out.println("anonim(null)    GET /rapor       -> "+decide(a,null,"/rapor"));
  System.out.println("--- zincir B: /** once, /yonetim/** sonra ---");
  System.out.println("ayse[RAPOR_OKU] GET /yonetim/sil -> "+decide(b,ayse,"/yonetim/sil"));
  System.out.println("--- hasRole / hasAuthority ---");
  for(String authority:List.of("YONETICI","ROLE_YONETICI")){
   var auth=user("u",authority);
   System.out.println("yetki="+String.format("%-14s",authority)+" hasRole(YONETICI)      -> "+(AuthorityAuthorizationManager.hasRole("YONETICI").authorize(()->auth,new Object()).isGranted()?"IZIN":"RED"));
   System.out.println("yetki="+String.format("%-14s",authority)+" hasAuthority(YONETICI) -> "+(AuthorityAuthorizationManager.hasAuthority("YONETICI").authorize(()->auth,new Object()).isGranted()?"IZIN":"RED"));
  }
  try(var ctx=new AnnotationConfigApplicationContext(Config.class)){
   var s=ctx.getBean(Servis.class);
   System.out.println("--- metot yetkilendirme (bean proxy mi: "+AopUtils.isAopProxy(s)+") ---");
   SecurityContextHolder.getContext().setAuthentication(ayse);
   System.out.println("ayse[RAPOR_OKU] rapor()     -> "+call(s::rapor));
   System.out.println("ayse[RAPOR_OKU] belge(ayse) -> "+call(()->s.belge("ayse")));
   System.out.println("ayse[RAPOR_OKU] belge(can)  -> "+call(()->s.belge("can")));
   SecurityContextHolder.getContext().setAuthentication(mdr);
   System.out.println("mdr[YONETICI]   rapor()     -> "+call(s::rapor));
   System.out.println("mdr[YONETICI]   dolayli()   -> "+call(s::dolayli));
  }finally{SecurityContextHolder.clearContext();}
 }
}
