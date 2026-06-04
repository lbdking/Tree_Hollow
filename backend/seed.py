"""初始化数据库 + 灌入测试数据"""
import json
from datetime import datetime, timedelta, date

from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models.appointment import Counselor
from app.models.content import Article, MoodRecord
from app.models.group import GroupActivity, GroupMember, SupportGroup
from app.models.hollow import HollowPost, HollowReply
from app.models.user import User


def init_db():
    import app.models  # noqa
    Base.metadata.create_all(bind=engine)


def seed():
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            print("数据库已初始化，跳过 seed。")
            return

        admin = User(student_id="admin", password_hash=hash_password("admin123"), real_name="管理员", role="admin")
        student1 = User(student_id="2024001", password_hash=hash_password("123456"), real_name="李同学", role="student")
        student2 = User(student_id="2024002", password_hash=hash_password("123456"), real_name="王同学", role="student")
        student3 = User(student_id="2024003", password_hash=hash_password("123456"), real_name="张同学", role="student")
        c_user1 = User(student_id="counselor01", password_hash=hash_password("123456"), real_name="陈老师", role="counselor")
        c_user2 = User(student_id="counselor02", password_hash=hash_password("123456"), real_name="林老师", role="counselor")
        db.add_all([admin, student1, student2, student3, c_user1, c_user2])
        db.commit()

        # 咨询师档案
        slots = [
            {"date": (date.today() + timedelta(days=i)).isoformat(), "times": ["10:00", "14:00", "16:00"]}
            for i in range(1, 6)
        ]
        c1 = Counselor(
            user_id=c_user1.id,
            name="陈雨晴",
            title="国家二级心理咨询师",
            avatar="",
            expertise="焦虑,抑郁,人际关系",
            introduction="拥有 8 年高校心理咨询经验，擅长青少年情绪管理。",
            available_slots=json.dumps(slots, ensure_ascii=False),
            rating=5,
        )
        c2 = Counselor(
            user_id=c_user2.id,
            name="林知言",
            title="校园心理老师",
            avatar="",
            expertise="学业压力,睡眠,自我成长",
            introduction="温柔耐心的倾听者，相信每个人都拥有自愈的力量。",
            available_slots=json.dumps(slots, ensure_ascii=False),
            rating=5,
        )
        db.add_all([c1, c2])
        db.commit()

        # 科普
        articles = [
            Article(title="缓解焦虑的 5 个小方法", category="焦虑", summary="日常可上手的 5 个减压技巧。",
                    content="1. 深呼吸\n2. 写情绪日记\n3. 短时运动\n4. 与朋友聊聊\n5. 减少咖啡因\n\n每一个小动作，都是给自己温柔的礼物。",
                    cover="https://images.unsplash.com/photo-1499209974431-9dddcece7f88?w=800"),
            Article(title="抑郁不是你的错", category="抑郁", summary="理解抑郁，帮助自己也帮助他人。",
                    content="抑郁是一种疾病，不是性格弱点。如果你或身边的人正在经历持续的情绪低落，请不要责怪自己，及时寻求专业帮助。",
                    cover="https://images.unsplash.com/photo-1499728603263-13726abce5fd?w=800"),
            Article(title="改善睡眠的科学方法", category="睡眠",
                    summary="掌握睡眠的黄金法则。",
                    content="保持规律作息，避免睡前蓝光，做几次深呼吸，让身心慢下来……",
                    cover="https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?w=800"),
            Article(title="一段冥想引导视频", category="冥想", content_type="video",
                    summary="跟随声音放松你的身心。",
                    video_url="https://www.w3schools.com/html/mov_bbb.mp4",
                    cover="https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=800"),
            Article(title="如何与情绪共处", category="自我成长",
                    summary="情绪不是敌人。",
                    content="情绪如潮水，有起有落。允许它们来，也允许它们走。",
                    cover="https://images.unsplash.com/photo-1518837695005-2083093ee35b?w=800"),
        ]
        db.add_all(articles)
        db.commit()

        # 树洞帖子
        posts = [
            HollowPost(user_id=student1.id, content="今天答辩好紧张啊，手都在抖。但是同学们都鼓励我，感觉好暖。", mood_tag="紧张"),
            HollowPost(user_id=student2.id, content="最近失眠好严重，凌晨三点还在刷手机……", mood_tag="失眠"),
            HollowPost(user_id=student3.id, content="今天看到一只很可爱的小猫，心情突然变好了 🐱", mood_tag="开心"),
            HollowPost(user_id=student1.id, content="家人不理解我，感觉好孤独。", mood_tag="孤独"),
        ]
        db.add_all(posts)
        db.commit()

        replies = [
            HollowReply(post_id=posts[0].id, user_id=student2.id, content="加油呀！紧张说明你认真对待，相信你已经很棒了 🌟"),
            HollowReply(post_id=posts[0].id, user_id=student3.id, content="深呼吸，慢慢来。我们都在！"),
            HollowReply(post_id=posts[1].id, user_id=student3.id, content="试试睡前听轻音乐，关掉手机~ 抱抱你"),
            HollowReply(post_id=posts[3].id, user_id=student2.id, content="你不孤独，这里有很多人懂你的感受 💗"),
        ]
        db.add_all(replies)
        for r in replies:
            p = db.query(HollowPost).filter(HollowPost.id == r.post_id).first()
            if p:
                p.reply_count += 1
        db.commit()

        # 互助小组
        groups = [
            SupportGroup(name="考研减压互助组", topic="学业", description="一起聊聊考研路上的疲惫与希望。",
                         created_by=admin.id, member_count=1,
                         cover="https://images.unsplash.com/photo-1517048676732-d65bc937f952?w=800"),
            SupportGroup(name="失眠夜聊室", topic="失眠", description="睡不着的夜晚，我们陪你。",
                         created_by=admin.id, member_count=1,
                         cover="https://images.unsplash.com/photo-1519791883288-dc8bd696e667?w=800"),
            SupportGroup(name="社恐成长营", topic="人际",
                         description="慢慢来，没关系。", created_by=admin.id, member_count=1,
                         cover="https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?w=800"),
        ]
        db.add_all(groups)
        db.commit()

        for g in groups:
            db.add(GroupMember(group_id=g.id, user_id=admin.id, role="owner"))
        db.commit()

        # 活动
        activities = [
            GroupActivity(
                group_id=groups[0].id,
                title="考研冲刺答疑会",
                description="资深学长姐分享备考经验。",
                location="线上腾讯会议",
                start_time=datetime.utcnow() + timedelta(days=2, hours=10),
                end_time=datetime.utcnow() + timedelta(days=2, hours=12),
                capacity=30,
            ),
            GroupActivity(
                group_id=groups[1].id,
                title="深夜放松冥想",
                description="一起做 30 分钟睡前冥想。",
                location="线上",
                start_time=datetime.utcnow() + timedelta(days=1, hours=22),
                end_time=datetime.utcnow() + timedelta(days=1, hours=22, minutes=30),
                capacity=50,
            ),
        ]
        db.add_all(activities)
        db.commit()

        # 情绪打卡
        moods = [
            MoodRecord(user_id=student1.id, record_date=date.today() - timedelta(days=i),
                       mood=["😀", "😐", "😢", "😣", "🥰", "😴", "😌"][i % 7], score=(i % 5) + 1, note="")
            for i in range(7)
        ]
        db.add_all(moods)
        db.commit()

        print("✅ Seed 完成")
        print("默认账号：")
        print("  管理员    admin / admin123")
        print("  学生      2024001 / 123456")
        print("  学生      2024002 / 123456")
        print("  学生      2024003 / 123456")
        print("  咨询师    counselor01 / 123456 (陈雨晴)")
        print("  咨询师    counselor02 / 123456 (林知言)")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    seed()
