from typing import List, Optional


def _get_parser():
    try:
        from tree_sitter import Parser
        from tree_sitter_languages import get_language
        p = Parser()
        p.set_language(get_language("php"))
        return p
    except Exception:
        return None


def _node_text(text: bytes, node) -> str:
    return text[node.start_byte:node.end_byte].decode(errors="ignore")


def analyze(text: str):
    parser = _get_parser()
    if not parser:
        return None
    b = text.encode()
    tree = parser.parse(b)
    root = tree.root_node
    results = []
    def walk(n):
        for i in range(n.child_count):
            c = n.child(i)
            if c.type == "class_declaration":
                cname = None
                for j in range(c.child_count):
                    cc = c.child(j)
                    if cc.type == "name":
                        cname = _node_text(b, cc)
                        break
                methods = []
                properties = []
                for j in range(c.child_count):
                    cc = c.child(j)
                    if cc.type == "property_declaration":
                        for k in range(cc.child_count):
                            ck = cc.child(k)
                            if ck.type == "variable_name":
                                properties.append(_node_text(b, ck).lstrip("$"))
                    if cc.type == "method_declaration":
                        mname = None
                        body = None
                        for k in range(cc.child_count):
                            ck = cc.child(k)
                            if ck.type == "name":
                                mname = _node_text(b, ck)
                            if ck.type == "compound_statement":
                                body = ck
                        if mname:
                            calls = []
                            uses = []
                            sinks = []
                            if body:
                                stack = [body]
                                while stack:
                                    x = stack.pop()
                                    for t in range(x.child_count):
                                        y = x.child(t)
                                        if y.type == "function_call_expression":
                                            fn = None
                                            for u in range(y.child_count):
                                                z = y.child(u)
                                                if z.type in ("name", "qualified_name"):
                                                    fn = _node_text(b, z)
                                                    break
                                            if fn:
                                                calls.append(fn)
                                        if y.type in ("member_access_expression", "property_access_expression"):
                                            for u in range(y.child_count):
                                                z = y.child(u)
                                                if z.type == "variable_name":
                                                    v = _node_text(b, z)
                                                    if v.startswith("$this->"):
                                                        uses.append(v.split("->")[-1])
                                        stack.append(y)
                            methods.append({
                                "name": mname,
                                "line": body.start_point[0] + 1 if body else 1,
                                "calls": calls,
                                "uses": list(sorted(set(uses))),
                            })
                results.append({
                    "name": cname or "",
                    "methods": methods,
                    "properties": properties,
                })
            walk(c)
    walk(root)
    return results
