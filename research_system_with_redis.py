def cache_researcher(name):
    # أول شي نحاول نجيب البيانات من Redis
    data = r.get(f"researcher:{name}")
    if data:
        print("✅ تم جلب البيانات من Redis (Cache)")
        return eval(data)  # تحويل string لقاموس

    # إذا مش موجودة، نجيبها من MongoDB
    researcher = researchers_col.find_one({"name": name})
    if not researcher:
        return None

    # نخزنها في Redis لمدة 60 ثانية مثلاً
    r.set(f"researcher:{name}", str(researcher), ex=60)
    print("✅ تم جلب البيانات من MongoDB وتم تخزينها في Redis")
    return researcher
