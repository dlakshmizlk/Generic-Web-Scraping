#!/usr/bin/env python3
"""
Daily URL Scraper - Main Script

This script scrapes URLs from multiple sources, tracks them in a JSON file,
and emails only new URLs that haven't been seen before.

Usage:
    python main.py
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from src.logger import setup_logger
from src.storage import URLStorage
from src.joinclassactions_scraper import JoinClassActionsScraper
from src.rankiteo_scraper import RankiteoScraper
from src.dexpose_scraper import DexposeScraper  # NEW
from src.cybersecguru_scraper import CyberSecGuruScraper  # NEW
from src.email_sender import EmailSender


def main():
    """Main execution function."""
    # Setup logger
    logger = setup_logger('url_scraper', config.LOGS_DIR)
    
    logger.info("="*70)
    logger.info("Starting Daily URL Scraper")
    logger.info("="*70)
    
    try:
        # Validate configuration
        logger.info("Validating configuration...")
        config.validate_config()
        logger.info("Configuration validated successfully")
        
        # Initialize components
        logger.info("\nInitializing components...")
        
        # Separate storage for each source - ADD TWO NEW STORAGE
        joinclassactions_storage = URLStorage(config.JOINCLASSACTIONS_URLS_FILE, logger)
        rankiteo_storage = URLStorage(config.RANKITEO_URLS_FILE, logger)
        dexpose_storage = URLStorage(config.DEXPOSE_URLS_FILE, logger)  # NEW
        cybersecguru_storage = URLStorage(config.CYBERSECGURU_URLS_FILE, logger)  # NEW
        
        # Initialize all scrapers - ADD TWO NEW SCRAPERS
        joinclassactions_scraper = JoinClassActionsScraper(
            logger=logger,
            timeout=config.REQUEST_TIMEOUT,
            max_retries=config.MAX_RETRIES,
            retry_delay=config.RETRY_DELAY
        )
        rankiteo_scraper = RankiteoScraper(
            logger=logger,
            timeout=config.REQUEST_TIMEOUT,
            max_retries=config.MAX_RETRIES,
            retry_delay=config.RETRY_DELAY
        )
        dexpose_scraper = DexposeScraper(  # NEW
            logger=logger,
            timeout=config.REQUEST_TIMEOUT,
            max_retries=config.MAX_RETRIES,
            retry_delay=config.RETRY_DELAY
        )
        cybersecguru_scraper = CyberSecGuruScraper(  # NEW
            logger=logger,
            timeout=config.REQUEST_TIMEOUT,
            max_retries=config.MAX_RETRIES,
            retry_delay=config.RETRY_DELAY
        )
        
        email_sender = EmailSender(
            smtp_server=config.SMTP_SERVER,
            smtp_port=config.SMTP_PORT,
            username=config.SMTP_USERNAME,
            password=config.SMTP_PASSWORD,
            from_email=config.EMAIL_FROM,
            logger=logger
        )
        
        # Show current stats - UPDATE TO SHOW ALL 4 SOURCES
        joinclassactions_stats = joinclassactions_storage.get_stats()
        rankiteo_stats = rankiteo_storage.get_stats()
        dexpose_stats = dexpose_storage.get_stats()  # NEW
        cybersecguru_stats = cybersecguru_storage.get_stats()  # NEW
        
        total_urls = (joinclassactions_stats['total_urls'] + 
                     rankiteo_stats['total_urls'] + 
                     dexpose_stats['total_urls'] + 
                     cybersecguru_stats['total_urls'])
        
        logger.info(f"\nCurrent storage stats:")
        logger.info(f"  JoinClassActions URLs: {joinclassactions_stats['total_urls']}")
        logger.info(f"  Rankiteo URLs: {rankiteo_stats['total_urls']}")
        logger.info(f"  Dexpose URLs: {dexpose_stats['total_urls']}")  # NEW
        logger.info(f"  CyberSecGuru URLs: {cybersecguru_stats['total_urls']}")  # NEW
        logger.info(f"  Total URLs tracked: {total_urls}")
        
        # Scrape all sources
        logger.info("\n" + "="*70)
        logger.info("Starting URL scraping...")
        logger.info("="*70)
        
        # ADD TWO NEW SCRAPERS TO THE DICT
        try:
            scraped_urls = {
                "classactions_sitemap": joinclassactions_scraper.scrape(),
                "rankiteo_blog": rankiteo_scraper.scrape(),
                "dexpose": dexpose_scraper.scrape(),  # NEW
                "cybersecguru": cybersecguru_scraper.scrape()  # NEW
            }
        finally:
            joinclassactions_scraper.close()
            rankiteo_scraper.close()
            dexpose_scraper.close()  # NEW
            cybersecguru_scraper.close()  # NEW
        
        # Process results and identify new URLs
        logger.info("\n" + "="*70)
        logger.info("Processing results...")
        logger.info("="*70)
        
        new_urls_by_source = {}
        total_scraped = 0
        total_new = 0
        
        # Process JoinClassActions URLs
        source_name = "classactions_sitemap"
        urls = scraped_urls[source_name]
        total_scraped += len(urls)
        
        if urls:
            new_urls = joinclassactions_storage.add_urls(urls)
            new_urls_by_source[source_name] = new_urls
            total_new += len(new_urls)
            
            logger.info(f"\n{source_name}:")
            logger.info(f"  Scraped: {len(urls)} URLs")
            logger.info(f"  New: {len(new_urls)} URLs")
        else:
            logger.info(f"\n{source_name}: No URLs found")
            new_urls_by_source[source_name] = []
        
        # Process Rankiteo URLs
        source_name = "rankiteo_blog"
        urls = scraped_urls[source_name]
        total_scraped += len(urls)
        
        if urls:
            new_urls = rankiteo_storage.add_urls(urls)
            new_urls_by_source[source_name] = new_urls
            total_new += len(new_urls)
            
            logger.info(f"\n{source_name}:")
            logger.info(f"  Scraped: {len(urls)} URLs")
            logger.info(f"  New: {len(new_urls)} URLs")
        else:
            logger.info(f"\n{source_name}: No URLs found")
            new_urls_by_source[source_name] = []
        
        # Process Dexpose URLs - NEW SECTION
        source_name = "dexpose"
        urls = scraped_urls[source_name]
        total_scraped += len(urls)
        
        if urls:
            new_urls = dexpose_storage.add_urls(urls)
            new_urls_by_source[source_name] = new_urls
            total_new += len(new_urls)
            
            logger.info(f"\n{source_name}:")
            logger.info(f"  Scraped: {len(urls)} URLs")
            logger.info(f"  New: {len(new_urls)} URLs")
        else:
            logger.info(f"\n{source_name}: No URLs found")
            new_urls_by_source[source_name] = []
        
        # Process CyberSecGuru URLs - NEW SECTION
        source_name = "cybersecguru"
        urls = scraped_urls[source_name]
        total_scraped += len(urls)
        
        if urls:
            new_urls = cybersecguru_storage.add_urls(urls)
            new_urls_by_source[source_name] = new_urls
            total_new += len(new_urls)
            
            logger.info(f"\n{source_name}:")
            logger.info(f"  Scraped: {len(urls)} URLs")
            logger.info(f"  New: {len(new_urls)} URLs")
        else:
            logger.info(f"\n{source_name}: No URLs found")
            new_urls_by_source[source_name] = []
        
        # Summary - UPDATE TO SHOW ALL 4 SOURCES
        logger.info("\n" + "="*70)
        logger.info("SUMMARY")
        logger.info("="*70)
        logger.info(f"Total URLs scraped: {total_scraped}")
        logger.info(f"New URLs found: {total_new}")
        logger.info(f"Total JoinClassActions URLs in storage: {joinclassactions_storage.get_stats()['total_urls']}")
        logger.info(f"Total Rankiteo URLs in storage: {rankiteo_storage.get_stats()['total_urls']}")
        logger.info(f"Total Dexpose URLs in storage: {dexpose_storage.get_stats()['total_urls']}")  # NEW
        logger.info(f"Total CyberSecGuru URLs in storage: {cybersecguru_storage.get_stats()['total_urls']}")  # NEW
        
        grand_total = (joinclassactions_storage.get_stats()['total_urls'] + 
                      rankiteo_storage.get_stats()['total_urls'] + 
                      dexpose_storage.get_stats()['total_urls'] + 
                      cybersecguru_storage.get_stats()['total_urls'])
        logger.info(f"Grand total URLs in storage: {grand_total}")
        
        # Send email if there are new URLs (or always send daily report)
        logger.info("\n" + "="*70)
        logger.info("Sending email report...")
        logger.info("="*70)
        
        if total_new > 0:
            logger.info(f"Found {total_new} new URL(s). Sending email...")
            success = email_sender.send_report(config.EMAIL_TO, new_urls_by_source)
            
            if success:
                logger.info("Email sent successfully!")
            else:
                logger.error("Failed to send email")
                return 1
        else:
            logger.info("No new URLs found today. Sending notification email...")
            success = email_sender.send_report(config.EMAIL_TO, new_urls_by_source)
            
            if success:
                logger.info("Notification email sent successfully!")
            else:
                logger.error("Failed to send email")
                return 1
        
        logger.info("\n" + "="*70)
        logger.info("Daily URL scraper completed successfully!")
        logger.info("="*70)
        
        return 0
        
    except ValueError as e:
        logger.error(f"\nConfiguration error: {e}")
        return 1
    except KeyboardInterrupt:
        logger.warning("\n\nInterrupted by user")
        return 130
    except Exception as e:
        logger.error(f"\nUnexpected error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())