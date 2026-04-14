"""
자동화 에이전트 (agent_automation.py)
역할: 수집 → 비교 → 게시 파이프라인 오케스트레이터
n8n Webhook에서 호출하거나 직접 실행 가능
"""

import sys
import json
import logging
from datetime import datetime

# 같은 폴더의 에이전트 임포트
import agent_collector
import agent_comparator
import agent_publisher

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'logs/run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8')
    ]
)
log = logging.getLogger(__name__)

def run_pipeline() -> dict:
    """
    전체 파이프라인 실행
    Returns: { status, collected, new_count, published, errors }
    """
    log.info("=" * 50)
    log.info("대학활동 자동 수집 파이프라인 시작")
    log.info("=" * 50)

    result = {
        'status': 'success',
        'collected': 0,
        'new_count': 0,
        'published': 0,
        'failed': 0,
        'errors': [],
        'started_at': datetime.now().isoformat()
    }

    try:
        # Step 1: 수집
        log.info("▶ Step 1: 수집 에이전트 실행")
        collected = agent_collector.run()
        result['collected'] = len(collected)
        log.info(f"  수집 완료: {len(collected)}개")

        if not collected:
            log.warning("수집된 게시글이 없습니다. 파이프라인 종료.")
            result['message'] = '수집된 게시글 없음'
            return result

        # Step 2: 중복 제거
        log.info("▶ Step 2: 비교 에이전트 실행")
        new_posts = agent_comparator.run(collected)
        result['new_count'] = len(new_posts)
        log.info(f"  신규 게시글: {len(new_posts)}개 (중복 {len(collected) - len(new_posts)}개 제거)")

        if not new_posts:
            log.info("신규 게시글이 없습니다. 게시 단계 생략.")
            result['message'] = '신규 게시글 없음 (모두 중복)'
            return result

        # Step 3: 게시
        log.info("▶ Step 3: 게시 에이전트 실행")
        pub_result = agent_publisher.run(new_posts)
        result['published'] = pub_result['success']
        result['failed'] = pub_result['failed']
        result['errors'].extend(pub_result['errors'])

        log.info(f"  게시 완료: {pub_result['success']}개 / 실패: {pub_result['failed']}개")

    except Exception as e:
        error_msg = f"파이프라인 오류: {type(e).__name__}: {e}"
        log.error(f"❌ {error_msg}")
        result['status'] = 'error'
        result['errors'].append(error_msg)

    finally:
        result['finished_at'] = datetime.now().isoformat()
        log.info("=" * 50)
        log.info(f"파이프라인 완료 | 상태: {result['status']}")
        log.info(f"  수집: {result['collected']}개 → 신규: {result['new_count']}개 → 게시: {result['published']}개")
        if result['errors']:
            log.error(f"  오류 목록:")
            for err in result['errors']:
                log.error(f"    - {err}")
        log.info("=" * 50)

    return result

if __name__ == '__main__':
    import os
    os.makedirs('logs', exist_ok=True)

    result = run_pipeline()

    # n8n으로 결과 반환 (JSON stdout)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # 오류 발생 시 종료 코드 1
    if result['status'] == 'error':
        sys.exit(1)
