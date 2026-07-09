import json
import os

TOOLS_FILE = "config/tools.json"

GITHUB_TOOLS = [
    {"name": "AuditLuma-AI代码审计系统", "url": "https://github.com/Vistaminc/AuditLuma", "description": "AI代码审计系统（智能体）"},
    {"name": "AI-Infra-Guard", "url": "https://github.com/Tencent/AI-Infra-Guard/", "description": "AI检测工具（检测AI是否安全）"},
    {"name": "GoPhish", "url": "https://github.com/gophish/gophish/", "description": "钓鱼测试工具"},
    {"name": "sourcefare", "url": "https://sourcefare.tiklab.net/", "description": "代码审计"},
    {"name": "DeepAudit", "url": "https://github.com/lintsinghua/DeepAudit", "description": "代码审计"},
    {"name": "CyberStrikeAI", "url": "https://github.com/Ed1s0nZ/CyberStrikeAI", "description": "AI渗透测试辅助工具"},
    {"name": "Strix", "url": "https://github.com/usestrix/strix", "description": "开源的AI安全测试工具"},
    {"name": "HexStrike AI", "url": "https://github.com/0x4m4/hexstrike-ai/", "description": "HexStrike AI"},
    {"name": "ScopeSentry", "url": "https://github.com/Autumn-27/ScopeSentry/blob/main/README_CN.md", "description": "资产探测"},
    {"name": "Sirius", "url": "https://github.com/SiriusScan/Sirius", "description": "漏扫"},
    {"name": "AllinSSL", "url": "https://github.com/allinssl/allinssl", "description": "AllinSSL"},
    {"name": "Vulhub", "url": "https://vulhub.org/zh", "description": "靶场漏洞复现平台"},
    {"name": "TestNet", "url": "https://github.com/testnet0/testnet", "description": "资产探测"},
    {"name": "MemShellParty", "url": "https://github.com/ReaJason/MemShellParty", "description": "MemShellParty"},
    {"name": "java-chains", "url": "https://github.com/vulhub/java-chains/releases/latest", "description": "java-chains"},
    {"name": "Robin", "url": "https://github.com/apurvsinghgautam/robin/", "description": "Robin"},
    {"name": "XingRin(星环)", "url": "https://github.com/yyhuni/xingrin", "description": "XingRin(星环)"},
    {"name": "higress ai网关", "url": "https://higress.ai/", "description": "higress ai网关"},
    {"name": "ApolloFish", "url": "https://github.com/safe1024/apollofish-template", "description": "ApolloFish"},
    {"name": "BeforeDawn", "url": "https://github.com/rabbitmask/BeforeDawn-docker", "description": "BeforeDawn"},
    {"name": "BrutDroid", "url": "https://github.com/Brut-Security/BrutDroid/", "description": "APP检测"},
    {"name": "AppScan", "url": "https://appscan.ly.com/user-guide/download/", "description": "AppScan"},
    {"name": "fscan", "url": "https://github.com/shadow1ng/fscan", "description": "内网综合扫描工具"},
    {"name": "goby", "url": "https://gobysec.net/", "description": "goby"},
    {"name": "linuxmirrors", "url": "https://linuxmirrors.cn/", "description": "linuxmirrors"},
    {"name": "问脉", "url": "https://github.com/chaitin/veinmind-tools", "description": "问脉"},
    {"name": "应急响应手册", "url": "https://book.noptrace.com/#pdf", "description": "应急响应手册"},
    {"name": "AIFuzzing", "url": "https://github.com/darkfiv/AIFuzzing", "description": "AIFuzzing"},
    {"name": "DudeSuite", "url": "https://www.dudesuite.cn/", "description": "DudeSuite"},
    {"name": "appshark", "url": "https://github.com/bytedance/appshark", "description": "appshark"},
    {"name": "GoDLP", "url": "https://github.com/bytedance/godlp", "description": "GoDLP"},
    {"name": "承影", "url": "https://github.com/yhy0/ChYing", "description": "承影"},
    {"name": "Rscan", "url": "https://github.com/CRlife/Rscan", "description": "Rscan"},
    {"name": "深眼deepEye", "url": "https://github.com/zakirkun/deep-eye", "description": "深眼deepEye"},
    {"name": "FastAIE", "url": "https://github.com/vam876/FastAIE/releases/", "description": "FastAIE"},
    {"name": "GHOSTCREW", "url": "https://github.com/killvxk/ghostcrew-GH05TCREW", "description": "GHOSTCREW"},
    {"name": "hexstrike_mcp", "url": "https://github.com/0x4m4/hexstrike-ai.git", "description": "hexstrike_mcp"},
    {"name": "Shannon", "url": "https://github.com/KeygraphHQ/shannon", "description": "Shannon"},
    {"name": "Tscan无影", "url": "https://github.com/TideSec/TscanPlus", "description": "Tscan无影"},
    {"name": "密探", "url": "https://github.com/kkbo8005/mitan", "description": "密探"},
    {"name": "Virgol", "url": "https://github.com/VirgoLee/Virgol?tab=readme-ov-file", "description": "Virgol"},
    {"name": "PrismX棱镜单兵系统", "url": "https://github.com/yqcs/prismx", "description": "PrismX棱镜单兵系统"},
    {"name": "统领Online_tools", "url": "https://github.com/CuriousLearnerDev/Online_tools", "description": "统领Online_tools"},
    {"name": "次元剑", "url": "https://github.com/soevai/MetaSword", "description": "次元剑"},
    {"name": "EasyTools", "url": "https://github.com/doki-byte/EasyTools.git", "description": "EasyTools"},
    {"name": "Railgun", "url": "https://github.com/lz520520/railgun", "description": "Railgun"},
    {"name": "Slack", "url": "https://github.com/qiwentaidi/Slack/", "description": "Slack"},
    {"name": "First", "url": "https://github.com/Spade-sec/First?tab=readme-ov-file", "description": "First"},
    {"name": "BurpSuit", "url": "https://www.52pojie.cn/thread-1544866-1-1.html", "description": "BurpSuit"},
    {"name": "Yakit", "url": "https://www.yaklang.com/", "description": "Yakit"},
    {"name": "Fiddler", "url": "https://www.telerik.com/download/fiddler", "description": "Fiddler"},
    {"name": "Wpe网络封包拦截器", "url": "https://www.wpe64.com/", "description": "Wpe网络封包拦截器"},
    {"name": "Reqable", "url": "https://reqable.com/zh-CN/", "description": "Reqable"},
    {"name": "fir-proxy", "url": "https://github.com/11firefly11/fir-proxy", "description": "fir-proxy"},
    {"name": "Charles", "url": "https://www.charlesproxy.com/", "description": "Charles"},
    {"name": "Proxifier", "url": "https://www.proxifier.com/", "description": "Proxifier"},
    {"name": "ngrok", "url": "http://ngrok.com/download", "description": "ngrok"},
    {"name": "WebSocketReflectorX", "url": "https://github.com/XDSEC/WebSocketReflectorX", "description": "WebSocketReflectorX"},
    {"name": "SakuraFrp", "url": "https://www.natfrp.com/tunnel/download", "description": "SakuraFrp"},
    {"name": "befree", "url": "https://github.com/zidanfanshao/befree", "description": "befree"},
    {"name": "飞鱼IP代理池", "url": "https://www.feiyuip.com/download", "description": "飞鱼IP代理池"},
    {"name": "ProxyCat-V2.0.4", "url": "https://github.com/honmashironeko/ProxyCat/blob/main/ProxyCat-Manual/Operation%20Manual.md", "description": "ProxyCat-V2.0.4"},
    {"name": "YILU Proxy", "url": "https://yilusk5.com/cn/doc.html", "description": "YILU Proxy"},
    {"name": "suo5", "url": "https://github.com/zema1/suo5/releases", "description": "suo5"},
    {"name": "Venom", "url": "https://cn-sec.com/archives/4931878.html", "description": "Venom"},
    {"name": "reGeorg", "url": "https://github.com/sensepost/reGeorg", "description": "reGeorg"},
    {"name": "privoxy", "url": "https://www.silvester.org.uk/privoxy/Windows/", "description": "privoxy"},
    {"name": "pingtunnel", "url": "https://github.com/esrrhs/pingtunnel/releases", "description": "pingtunnel"},
    {"name": "Neo-reGeorg", "url": "https://github.com/L-codes/Neo-reGeorg", "description": "Neo-reGeorg"},
    {"name": "icmpsh", "url": "https://github.com/bdamele/icmpsh.git", "description": "icmpsh"},
    {"name": "Erfrp", "url": "https://github.com/Goqi/Erfrp", "description": "Erfrp"},
    {"name": "frp", "url": "https://github.com/fatedier/frp", "description": "frp"},
    {"name": "dnscat2", "url": "https://github.com/iagox86/dnscat2", "description": "dnscat2"},
    {"name": "cpolar", "url": "https://www.cpolar.com/", "description": "cpolar"},
    {"name": "Deadpool", "url": "https://github.com/thinkoaa/Deadpool", "description": "Deadpool"},
    {"name": "Fscan", "url": "https://github.com/shadow1ng/fscan", "description": "Fscan"},
    {"name": "FscanParser", "url": "https://github.com/teamdArk5/FscanParser", "description": "FscanParser"},
    {"name": "Qscan", "url": "https://github.com/qi4L/qscan", "description": "Qscan"},
    {"name": "GYscan", "url": "https://gyscan.space/", "description": "GYscan"},
    {"name": "CloneX", "url": "https://github.com/0x727/CloneX_0x727", "description": "CloneX"},
    {"name": "HackerPermKeeper", "url": "https://github.com/BrianBechtel/HackerPermKeeper/", "description": "HackerPermKeeper"},
    {"name": "CACM", "url": "https://github.com/RuoJi6/CACM/", "description": "CACM"},
    {"name": "impacket", "url": "https://github.com/SecureAuthCorp/impacket.git", "description": "impacket"},
    {"name": "iox", "url": "https://github.com/EddieIvan01/iox", "description": "iox"},
    {"name": "Kerbrute", "url": "https://github.com/ropnop/kerbrute", "description": "Kerbrute"},
    {"name": "Ladon拉东内网工具集", "url": "https://k8gege.org/Ladon/", "description": "Ladon拉东内网工具集"},
    {"name": "Procdump", "url": "https://learn.microsoft.com/en-us/sysinternals/downloads/procdump", "description": "Procdump"},
    {"name": "猕猴桃mimikatz", "url": "https://github.com/gentilkiwi/mimikatz/releases", "description": "猕猴桃mimikatz"},
    {"name": "pypykatz", "url": "https://github.com/skelsec/pypykatz.git", "description": "pypykatz"},
    {"name": "rathole", "url": "https://github.com/rathole-org/rathole/releases", "description": "rathole"},
    {"name": "RDPWrap", "url": "https://github.com/stascorp/rdpwrap", "description": "RDPWrap"},
    {"name": "RidHijack", "url": "https://github.com/yanghaoi/ridhijack", "description": "RidHijack"},
    {"name": "SchTask", "url": "https://github.com/0x727/SchTask_0x727/releases/tag/v1.0", "description": "SchTask"},
    {"name": "NetSonar", "url": "https://github.com/sn4k3/NetSonar/releases/", "description": "NetSonar"},
    {"name": "科来网络分析系统", "url": "https://www.colasoft.com.cn/downloads/csnas", "description": "科来网络分析系统"},
    {"name": "trafficeye攻击流量分析", "url": "https://github.com/CuriousLearnerDev/TrafficEye", "description": "trafficeye攻击流量分析"},
]

def add_tools():
    try:
        if os.path.exists(TOOLS_FILE):
            with open(TOOLS_FILE, 'r', encoding='utf-8') as f:
                tools = json.load(f)
        else:
            tools = []
        
        existing_urls = {t.get('url', '') for t in tools}
        
        new_tools = []
        for tool_info in GITHUB_TOOLS:
            if tool_info['url'] not in existing_urls:
                tool = {
                    "name": tool_info['name'],
                    "category": "网页工具/开源工具",
                    "type": "网页",
                    "description": tool_info['description'],
                    "weight": 0,
                    "url": tool_info['url'],
                    "path": "",
                    "params": "",
                    "tags": [],
                    "group": ""
                }
                new_tools.append(tool)
        
        tools.extend(new_tools)
        
        with open(TOOLS_FILE, 'w', encoding='utf-8') as f:
            json.dump(tools, f, ensure_ascii=False, indent=2)
        
        print(f"成功添加 {len(new_tools)} 个新工具")
        print(f"总工具数: {len(tools)}")
        
    except Exception as e:
        print(f"添加工具失败: {e}")

if __name__ == "__main__":
    add_tools()
